(() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropSymbols = Object.getOwnPropertySymbols;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __propIsEnum = Object.prototype.propertyIsEnumerable;
  var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
  var __spreadValues = (a, b) => {
    for (var prop in b || (b = {}))
      if (__hasOwnProp.call(b, prop))
        __defNormalProp(a, prop, b[prop]);
    if (__getOwnPropSymbols)
      for (var prop of __getOwnPropSymbols(b)) {
        if (__propIsEnum.call(b, prop))
          __defNormalProp(a, prop, b[prop]);
      }
    return a;
  };

  // ../lens_cpq/lens_cpq/public/design_configurator.bundle.js
  var clDesignConfigurator = class {
    constructor({ wrapper: iWrapper, page: iPage, frm: iFrm, design_configurator: iDesignConfigurator }) {
      this.$wrapper = $(iWrapper);
      this.page = iPage;
      this.design_configurator = iDesignConfigurator;
      this.frm = iFrm;
      this.fnMake();
      this.fnPrepareLayout();
      this.fnBindEvents();
    }
    fnMake() {
      let ldOptions = __spreadValues(__spreadValues({}, this.fnTreeOptions()), this.fnTreeMethods());
      frappe.views.trees["Design Configurator"] = new frappe.views.TreeView(ldOptions);
      let lNode = frappe.views.trees["Design Configurator"].tree.root_node;
      frappe.views.trees["Design Configurator"].tree.show_toolbar(lNode);
      frappe.views.trees["Design Configurator"].tree.load_children(lNode, true);
      this.tree_view = frappe.views.trees["Design Configurator"];
    }
    fnBindEvents() {
      frappe.views.trees["Design Configurator"].events = {
        frm: this.frm,
        load_tree: this.fnLoadTree
      };
    }
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
        do_not_setup_menu: true
      };
    }
    fnTreeMethods() {
      let lFrmObj = this;
      return {
        onload: function(iTreeView) {
          iTreeView.args["parent"] = lFrmObj.frm.doc.design_template;
          iTreeView.parent = lFrmObj.$wrapper.get(0);
          iTreeView.body = lFrmObj.$wrapper.get(0);
          iTreeView.make_tree();
        }
      };
    }
    fnPrepareLayout() {
      let lMainDiv = $(this.page)[0];
      lMainDiv.style.marginBottom = "15px";
      $(lMainDiv).find(".tree-children")[0].style.minHeight = "370px";
      $(lMainDiv).find(".tree-children")[0].style.maxHeight = "370px";
      $(lMainDiv).find(".tree-children")[0].style.overflowY = "auto";
    }
    fnLoadTree(iResponse, iNode) {
      frappe.views.trees["Design Configurator"].tree.load_children(iNode);
    }
  };
  frappe.ui.DesignConfigurator = clDesignConfigurator;
})();
//# sourceMappingURL=design_configurator.bundle.GTAJCVQO.js.map
