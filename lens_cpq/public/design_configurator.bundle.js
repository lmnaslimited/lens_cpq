// constructor: Initialize the design tree, layout, and events
// make: Build and display the tree structure with root and children
// bind_events: Attach tree events for editing and loading
// tree_options: Define tree configuration and behavior
// prepare_layout: Set tree container layout and scrolling
// load_tree: Load child nodes for a given tree node
// tree_methods: Define behavior when the tree loads
// frappe.ui.DesignConfigurator: Expose the class globally for use in forms

class DesignConfigurator {
	constructor({ wrapper, page, frm, design_configurator }) {
		this.$wrapper = $(wrapper);
		this.page = page;
		this.frm = frm;
		this.design_configurator = design_configurator;
		this.make();
		this.prepare_layout();
		this.bind_events();
	}
	make() {
		let ld_options = {
			...this.tree_options(),
			...this.tree_methods(),
		};

		frappe.views.trees["Design Configurator"] = new frappe.views.TreeView(ld_options);
		let l_node = frappe.views.trees["Design Configurator"].tree.root_node;
		frappe.views.trees["Design Configurator"].tree.show_toolbar(l_node);
		frappe.views.trees["Design Configurator"].tree.load_children(l_node, true);
		this.tree_view = frappe.views.trees["Design Configurator"];
	}
    bind_events() {
		frappe.views.trees["Design Configurator"].events = {
			frm: this.frm,
			edit_design: this.edit_design,
			load_tree: this.load_tree,
		};
	}
    tree_options() {
		return {
			parent: this.$wrapper.get(0),
			body: this.$wrapper.get(0),
			doctype: "Design Configurator",
			page: this.page,
			expandable: true,
			title: __("Design Configurator"),
			breadcrumb: "Manufacturing",
			get_tree_nodes: "lens_cpq.cpq.doctype.design.api.get_children",
			root_label: this.frm.doc.template_name,
			disable_add_node: true,
			get_tree_root: false,
			show_expand_all: false,
			extend_toolbar: false,
			do_not_make_page: true,
			do_not_setup_menu: true,
			
		};
	}
    prepare_layout() {
		let l_main_div = $(this.page)[0];

		l_main_div.style.marginBottom = "15px";
		$(l_main_div).find(".tree-children")[0].style.minHeight = "auto";
		$(l_main_div).find(".tree-children")[0].style.maxHeight = "auto";
		$(l_main_div).find(".tree-children")[0].style.overflowY = "auto";
	}
	load_tree(response, node) {
		frappe.views.trees["Design Configurator"].tree.load_children(node);
	}
	tree_methods() {
		let l_frm_obj = this;
		let l_view = frappe.views.trees["Design Configurator"]
		return {
			onload: function (me) {
				me.args["parent_id"] = l_frm_obj.frm.doc.name; 
				me.args["plant_floor"] = l_frm_obj.frm.doc.template_name;
				me.root_value = l_frm_obj.frm.doc.plant_floor;

				me.parent = l_frm_obj.$wrapper.get(0);
				me.body = l_frm_obj.$wrapper.get(0);
				me.make_tree();
			},
		}
	}
}
frappe.ui.DesignConfigurator = DesignConfigurator;