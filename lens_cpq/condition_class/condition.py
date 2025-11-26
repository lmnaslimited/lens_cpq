from abc import ABC, abstractmethod
from typing import Any, Dict, List
from lens_cpq.condition_class.input_condition_factory import InputFieldConditionFactory
from lens_cpq.condition_class.interface import IfCondtions
import frappe

# its an abstract class that implements IfCondtions
class ClCondtions(IfCondtions):
    def __init__(self, condition_type: str, doctype: str, event:str, fields: Dict[str, Any] = None):
        # self.condition_type = condition_type
        self.doctype = doctype
        self.fields = fields
        self.event = event

    def attach_model(self, view, model):
        self.model = model
        self.view = view
        
    def is_condition_true(self) -> bool:
        # print(f"[ClCondtions] Checking condition truth for {self.condition_type}")
        pass
    
    def evaluate_output(self):
        pass


    # FULL 4-STEP CHAIN RESOLUTION
    def resolve_condition_chain(self, field_name: str, value: Any):
        visited = set()
        collected = []
        current_field = field_name
        depth = 0  # to be deleted

        print(f"[Engine] Resolving chain for: {field_name} → {value}")

        while True:
            inp_records = self.model.fetch_input_sequence(current_field)
            if not inp_records:
                break

            # group by parent (each parent = one condition)
            parent = inp_records[0]["parent"]

            field_names = [inp["field_name"] for inp in inp_records]

            # if parent in visited:
            #     break

            if depth >= 2:
                break

            visited.add(parent)
            depth += 1

            if not self.view.is_value_present_in_doc(field_names):
                continue

            out_records = self.model.fetch_output_sequence(parent)
            if not out_records:
                break

            collected.append({
                "parent": parent,
                "input_records": inp_records,
                "output_records": out_records
            })

            # next field from output
            current_field = out_records[0]["field_name"]

        return collected

    # STEP 5–6: Organize Condition Types and Execute in Order
    def execute_conditions(self, chain_data: List[Dict]):
        """
        Execute conditions respecting both 'priority' and 'depends_on' relationships.
        chain_data: List of dicts with keys: 'parent', 'input_records', 'output_records'
        """

        print(f"[Engine] Running conditions for parents: {chain_data}")

        # ----------------------------------------
        # Fetch all condition headers from model
        # ----------------------------------------
        parent_names = list(set(c["parent"] for c in chain_data))
        condition_headers = self.model.fetch_condition_type(parent_names)

        # ----------------------------------------
        # Fast lookup for chain_data by parent
        # ----------------------------------------
        seq_map = {c["parent"]: c for c in chain_data}

        # ----------------------------------------
        # Build execution plan
        # ----------------------------------------
        execution_plan = []
        for hdr in condition_headers:
            parent = hdr["name"]
            if parent not in seq_map:
                # Skip conditions that have no input/output records
                continue
            seq = seq_map[parent]
            execution_plan.append({
                "header": hdr,
                "input": seq["input_records"],
                "output": seq["output_records"]
            })

        # ----------------------------------------
        # Build graph + indegree (dependency edges)
        # ----------------------------------------
        graph = {item["header"]["name"]: [] for item in execution_plan}
        indegree = {item["header"]["name"]: 0 for item in execution_plan}
        name_to_plan = {item["header"]["name"]: item for item in execution_plan}

        for item in execution_plan:
            hdr = item["header"]
            dep = hdr.get("depends_on")
            if dep:
                if dep not in graph:
                    # ignore unknown dependencies (not in current plan)
                    continue
                graph[dep].append(hdr["name"])
                indegree[hdr["name"]] += 1

        # ----------------------------------------
        # Kahn’s Topological Sort with priority
        # ----------------------------------------
        zero = [name_to_plan[n] for n in indegree if indegree[n] == 0]
        zero.sort(key=lambda x: x["header"]["priority"])

        sorted_order = []
        while zero:
            item = zero.pop(0)
            sorted_order.append(item)
            current = item["header"]["name"]

            for nxt in graph[current]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    zero.append(name_to_plan[nxt])
            zero.sort(key=lambda x: x["header"]["priority"])

        # ----------------------------------------
        # Execute in dependency + priority order
        # ----------------------------------------
        print("Execution order: " + ", ".join([i["header"]["name"] for i in sorted_order]))

        for item in sorted_order:
            hdr = item["header"]

            instance = InputFieldConditionFactory.build(
                cond_type=hdr["type"],
                cond_name=hdr["name"],
                input_records=item["input"],
                output_records=item["output"],
                engine=self
            )

            if instance.evaluate():
                instance.execute_output()
