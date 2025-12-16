from abc import ABC, abstractmethod
from typing import Any, Dict, List
# from lens_cpq.conditions.controller import FCViewModelFactory
from lens_cpq.conditions.input_condition_factory import cl_input_field_condition_factory
from lens_cpq.conditions.interface import if_condtions
import frappe

# its an abstract class that implements IfCondtions
class cl_condtions(if_condtions):
    def __init__(self, i_doctype: str, i_event:str, i_fields, id_view, id_model):
        # self.condition_type = condition_type
        self.l_doctype = i_doctype
        self.l_fields = i_fields
        self.l_event = i_event
        self.ld_model = id_model
        self.ld_view = id_view

    def is_condition_true(self) -> bool:
        # print(f"[ClCondtions] Checking condition truth for {self.condition_type}")
        pass
    
    def evaluate_output(self):
        pass
    

    # STEP 5–6: Organize Condition Types and Execute in Order
    def execute_conditions(self, ia_chain_data: List[Dict]):
        """
        Execute conditions respecting both 'priority' and 'depends_on' relationships.
        chain_data: List of dicts with keys: 'parent', 'input_records', 'output_records'
        """

        print(f"[Engine] Running conditions for parents: {ia_chain_data}")

        # ----------------------------------------
        # Fetch all condition headers from model
        # ----------------------------------------
        la_parent_names = list(set(c["parent"] for c in ia_chain_data))
        la_condition_headers = self.ld_model.fetch_condition_type(la_parent_names)

        # ----------------------------------------
        # Fast lookup for chain_data by parent
        # ----------------------------------------
        ld_seq_map = {c["parent"]: c for c in ia_chain_data}

        # ----------------------------------------
        # Build execution plan
        # ----------------------------------------
        la_execution_plan = []
        for ld_header in la_condition_headers:
            l_parent = ld_header["name"]
            if l_parent not in ld_seq_map:
                # Skip conditions that have no input/output records
                continue
            ld_seq = ld_seq_map[l_parent]
            la_execution_plan.append({
                "header": ld_header,
                "input": ld_seq["input_records"],
                "output": ld_seq["output_records"]
            })

        # ----------------------------------------
        # Build graph + indegree (dependency edges)
        # ----------------------------------------
        ld_graph = {id_item["header"]["name"]: [] for id_item in la_execution_plan}
        ld_indegree = {id_item["header"]["name"]: 0 for id_item in la_execution_plan}
        ld_name_to_plan = {id_item["header"]["name"]: id_item for id_item in la_execution_plan}

        for ld_item in la_execution_plan:
            ld_hdr = ld_item["header"]
            l_dep = ld_hdr.get("depends_on")
            if l_dep:
                if l_dep not in ld_graph:
                    # ignore unknown dependencies (not in current plan)
                    continue
                ld_graph[l_dep].append(ld_hdr["name"])
                ld_indegree[ld_hdr["name"]] += 1

        # ----------------------------------------
        # Kahn’s Topological Sort with priority
        # ----------------------------------------
        la_zero = [ld_name_to_plan[l_node] for l_node in ld_indegree if ld_indegree[l_node] == 0]
        la_zero.sort(key=lambda x: x["header"]["priority"])

        la_sorted_order = []
        while la_zero:
            ld_item = la_zero.pop(0)
            la_sorted_order.append(ld_item)
            current = ld_item["header"]["name"]

            for l_nxt in ld_graph[current]:
                ld_indegree[l_nxt] -= 1
                if ld_indegree[l_nxt] == 0:
                    la_zero.append(ld_name_to_plan[l_nxt])
            la_zero.sort(key=lambda x: x["header"]["priority"])

        # ----------------------------------------
        # Execute in dependency + priority order
        # ----------------------------------------
        print("Execution order: " + ", ".join([id_order["header"]["name"] for id_order in la_sorted_order]))

        for ld_item in la_sorted_order:
            ld_hdr = ld_item["header"]

            ld_instance = cl_input_field_condition_factory.build(
                i_cond_type=ld_hdr["type"],
                i_cond_name=ld_hdr["name"],
                ia_input_records=ld_item["input"],
                ia_output_records=ld_item["output"],
                io_engine=self
            )

            if ld_instance.evaluate():
                ld_instance.execute_output()
