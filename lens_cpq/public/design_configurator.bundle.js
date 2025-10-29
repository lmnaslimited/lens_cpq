class DesignConfigurator {
    constructor({ wrapper, page, frm, design_configurator }) {
        this.$wrapper = $(wrapper);
        this.page = page;
        this.design_configurator = design_configurator;
        this.frm = frm;

        this.make();
        this.prepare_layout();
        this.bind_events();
    }

    make() {
        let options = {
            ...this.tree_options(),
            ...this.tree_methods(),
        };

        frappe.views.trees["Design Configurator"] = new frappe.views.TreeView(options);
        let node = frappe.views.trees["Design Configurator"].tree.root_node;
        frappe.views.trees["Design Configurator"].tree.show_toolbar(node);
        frappe.views.trees["Design Configurator"].tree.load_children(node, true);
        this.tree_view = frappe.views.trees["Design Configurator"];
    }

    bind_events() {
        frappe.views.trees["Design Configurator"].events = {
            frm: this.frm,
            load_tree: this.load_tree,
        };
    }

    tree_options() {
        return {
            parent: this.$wrapper.get(0),
            body: this.$wrapper.get(0),
            doctype: "Design",
            page: this.page,
            expandable: true,
            title: __("Design Configurator"),
            breadcrumb: "Manufacturing",
            get_tree_nodes: "lens_cpq.cpq.doctype.design.api.fn_get_children",
            root_label: this.frm.doc.design_template,
            disable_add_node: true,
            get_tree_root: false,
            show_expand_all: false,
            extend_toolbar: false,
            do_not_make_page: true,
            do_not_setup_menu: true,
        };
    }

    tree_methods() {
        let frm_obj = this;
        let view = frappe.views.trees["Design Configurator"];

        return {
            onload: function (me) {
                // me.args["parent_id"] = frm_obj.frm.doc.name;
                me.args["parent"] = frm_obj.frm.doc.design_template;
                me.parent = frm_obj.$wrapper.get(0);
                me.body = frm_obj.$wrapper.get(0);
                me.make_tree();
            }
        };
    }

    prepare_layout() {
        let main_div = $(this.page)[0];

        main_div.style.marginBottom = "15px";
        $(main_div).find(".tree-children")[0].style.minHeight = "370px";
        $(main_div).find(".tree-children")[0].style.maxHeight = "370px";
        $(main_div).find(".tree-children")[0].style.overflowY = "auto";
    }

    load_tree(response, node) {
        frappe.views.trees["Design Configurator"].tree.load_children(node);
    }
}

frappe.ui.DesignConfigurator = DesignConfigurator;