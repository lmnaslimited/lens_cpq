class clDesignConfigurator {

    // Initializes the Design Configurator instance with form and layout details
    constructor({ wrapper: iWrapper, page: iPage, frm: iFrm, design_configurator: iDesignConfigurator }) {
        this.$wrapper = $(iWrapper);
        this.page = iPage;
        this.design_configurator = iDesignConfigurator;
        this.frm = iFrm;

        this.fnMake();
        this.fnPrepareLayout();
        this.fnBindEvents();
    }


    // Builds and initializes the TreeView 
    fnMake() {
        let ldOptions = {
            ...this.fnTreeOptions(),
            ...this.fnTreeMethods(),
        };

        frappe.views.trees["Design Configurator"] = new frappe.views.TreeView(ldOptions);
        let lNode = frappe.views.trees["Design Configurator"].tree.root_node;

        frappe.views.trees["Design Configurator"].tree.show_toolbar(lNode);
        frappe.views.trees["Design Configurator"].tree.load_children(lNode, true);
        this.tree_view = frappe.views.trees["Design Configurator"];
    }

    //  Binds custom events to the TreeView 
    fnBindEvents() {
        frappe.views.trees["Design Configurator"].events = {
            frm: this.frm,
            load_tree: this.fnLoadTree,
        };
    }

    //  Defines configuration options for the TreeView component
    fnTreeOptions() {
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

    // Defines methods and behaviors used by the TreeView during load and initialization
    fnTreeMethods() {
        let lFrmObj = this;

        return {
            onload: function (iTreeView) {
                iTreeView.args["parent"] = lFrmObj.frm.doc.design_template;
                iTreeView.parent = lFrmObj.$wrapper.get(0);
                iTreeView.body = lFrmObj.$wrapper.get(0);
                iTreeView.make_tree();
            }
        };
    }

    //  Prepares and styles the layout of the Design TreeView section 
    fnPrepareLayout() {
        let lMainDiv = $(this.page)[0];

        lMainDiv.style.marginBottom = "15px";
        $(lMainDiv).find(".tree-children")[0].style.minHeight = "370px";
        $(lMainDiv).find(".tree-children")[0].style.maxHeight = "370px";
        $(lMainDiv).find(".tree-children")[0].style.overflowY = "auto";
    }

    //  Loads child nodes dynamically when expanding a tree node
    fnLoadTree(iResponse, iNode) {
        frappe.views.trees["Design Configurator"].tree.load_children(iNode);
    }
}

// Register Design Configurator class globally within Frappe UI
frappe.ui.DesignConfigurator = clDesignConfigurator;