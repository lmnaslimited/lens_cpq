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
  var DesignConfigurator = class {
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
      let options = __spreadValues(__spreadValues({}, this.tree_options()), this.tree_methods());
      frappe.views.trees["Design Configurator"] = new frappe.views.TreeView(options);
      let node = frappe.views.trees["Design Configurator"].tree.root_node;
      frappe.views.trees["Design Configurator"].tree.show_toolbar(node);
      frappe.views.trees["Design Configurator"].tree.load_children(node, true);
      this.tree_view = frappe.views.trees["Design Configurator"];
    }
    bind_events() {
      frappe.views.trees["Design Configurator"].events = {
        frm: this.frm,
        edit_design: this.edit_design,
        load_tree: this.load_tree
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
        root_label: this.frm.doc.plant_floor,
        disable_add_node: true,
        get_tree_root: false,
        show_expand_all: false,
        extend_toolbar: false,
        do_not_make_page: true,
        do_not_setup_menu: true
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
    tree_methods() {
      let frm_obj = this;
      return {
        onload: function(me) {
          me.args["plant_floor"] = frm_obj.frm.doc.plant_floor;
          me.parent = frm_obj.$wrapper.get(0);
          me.body = frm_obj.$wrapper.get(0);
          me.make_tree();
        }
      };
    }
  };
  frappe.ui.DesignConfigurator = DesignConfigurator;
})();
//# sourceMappingURL=design_configurator.bundle.YETKVAY2.js.map
