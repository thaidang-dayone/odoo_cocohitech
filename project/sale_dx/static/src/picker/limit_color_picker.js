/** @odoo-module **/

import { ColorList } from "@web/core/colorlist/colorlist";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

import { Component } from "@odoo/owl";

export class LimitedColorPickerField extends Component {
    static template = "web.limitedColorPickerField";
    static components = {
        ColorList,
    };
    static props = {
        ...standardFieldProps,
        canToggle: { type: Boolean },
    };

    // Chỉ còn các màu 0, 1, 3 và 8
    static RECORD_COLORS = [0, 1, 3, 10];

    get isExpanded() {
        return !this.props.canToggle && !this.props.readonly;
    }

    // switchColor(colorIndex) {
    //     // Chỉ cho phép update nếu màu nằm trong danh sách cho phép
    //     if (this.constructor.RECORD_COLORS.includes(colorIndex)) {
    //         this.props.record.update({ [this.props.name]: colorIndex });
    //     }
    // }
    switchColor(colorIndex) {
        this.props.record.update({ [this.props.name]: colorIndex });
    }

}

export const limitedColorPickerField = {
    component: LimitedColorPickerField,
    supportedTypes: ["integer"],
    extractProps: ({ viewType }) => ({
        canToggle: viewType !== "list",
    }),
};

registry.category("fields").add("limited_color_picker", limitedColorPickerField);