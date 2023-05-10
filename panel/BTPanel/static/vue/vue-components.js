dynamic.delay('vue-components', () => {
                /**
                 * @description 定义请求是否为模型
                 * @type {String} 模型
                 */
                Vue.prototype.$request = bt.get_cookie('site_model') || 'java';
            
                /**
                 * @description 判断类型
                 * @param value {object} 判断的值
                 * @return {"undefined"|"boolean"|"number"|"string"|"function"|"symbol"|"bigint"|string}
                 */
                Vue.prototype.$isType = function (value) {
                    let type = typeof value;
                    switch (type) {
                        case 'object':
                            if (Array.isArray(value)) return 'array';
                            if (!value) return 'null';
                            return type;
                        default:
                            return type;
                    }
                };
            
                /**
                 * @description 请求封装
                 * @param keyMethod 接口名和loading，键值对
                 * @param param {object || function} 参数，可为空，为空则为callback参数
                 * @return {Promise<unknown>}
                 */
                Vue.prototype.$http = function (keyMethod, param) {
                    return new Promise((resolve, reject) => {
                        let method = Object.keys(keyMethod),
                            config = {
                                url: (this.$request && '/project/java/' + method[0]) || method[0],
                                data:
                                    (param &&
                                        this.$request && {
                                            data: JSON.stringify(param),
                                        }) ||
                                    param ||
                                    {},
                            },
                            success = function (res) {
                                resolve(res);
                            };
                        bt_tools.send(config, success, reject, {
                            load: keyMethod[method[0]],
                            verify: 'verify' in keyMethod ? keyMethod['verify'] : true,
                        });
                    });
                };
            
                /**
                 * @description shell 进度展示
                 * @param param {Object} {title:'提示内容'，执行的脚本信息}
                 * @return {c.index}
                 */
                Vue.prototype.$shell = function (param) {
                    return new Promise((resolve, reject) => {
                        layer.open({
                            type: 1,
                            title: param.title,
                            area: param.area,
                            btn: false,
                            closeBtn: false,
                            content:
                                '<div id="command_install_list" style="height: 100%;"><pre class="command_output_pre"  style="height: 100%;"></pre></div>',
                            success: (layers, indexs) => {
                                param.callback && param.callback(indexs);
                                try {
                                    bt_tools.command_line_output({
                                        el: '#command_install_list .command_output_pre',
                                        area: ['100%', '100%'],
                                        shell: param.shell,
                                        message: function (res) {
                                            if (res.indexOf('|-Successify --- 命令已执行! ---') > -1) {
                                                if (param.success) param.success(res);
                                                setTimeout(function () {
                                                    layer.close(indexs);
                                                    resolve();
                                                }, 100);
                                            }
                                        },
                                    });
                                } catch (e) {
                                    reject(e);
                                }
                            },
                        });
                    });
                };
            
                /**
                 * @description 异常抛出
                 * @return {Promise<unknown>}
                 */
                Vue.prototype.$tryCatch = function (code, error) {
                    try {
                        code();
                    } catch (e) {
                        // console.log(e)
                        this.$error(e);
                    }
                };
            
                /**
                 * @description 弹窗方法
                 * @param {Object} params layer配置
                 */
                Vue.prototype.$layer = function (params) {
                    return layer.open({
                        type: 1,
                        title: params.title,
                        area: params.area,
                        btn: false,
                        closeBtn: 2,
                        content: $(params.content),
                        success: params.success,
                        end: params.end,
                    });
                };
            
                /**
                 * @description 弹窗
                 * @param params {object} 配置
                 */
                Vue.prototype.$confirm = function (params) {
                    return new Promise((resolve, reject) => {
                        params.cancel = () => {
                            reject(false);
                        };
                        bt.confirm(
                            params,
                            async index => {
                                layer.close(index);
                                resolve(index);
                            },
                            () => {
                                reject(false);
                            }
                        );
                    });
                };
            
                /**
                 * @description 提示
                 * @param params {object} 配置
                 */
                Vue.prototype.$load = function (msg) {
                    return bt.load(msg);
                };
                /**
                 * @description 消息通道
                 * @param params
                 */
                Vue.prototype.$msg = function (params) {
                    let message = '',
                        icon = null;
                    if (typeof params === 'object') {
                        if ('msg' in params) {
                            message = params.msg;
                        } else if ('error_msg' in params) {
                            message = params.error_msg;
                        } else {
                            message = params.data;
                        }
                        if ('status' in params) icon = params.status ? 1 : 2;
                    }
                    if ('icon' in params) icon = params.icon;
                    layer.msg(message, {
                        icon: this.$isType(icon) === 'number' ? icon : 0,
                    });
                };
            
                /**
                 * @description 成功通知
                 * @param msg {string} 消息内容
                 * @param params {object} 配置参数
                 */
                Vue.prototype.$success = function (msg) {
                    this.$msg({
                        status: true,
                        msg: msg,
                    });
                };
            
                /**
                 * @description 错误通知
                 * @param msg {string} 消息内容
                 * @param params {object} 配置参数
                 */
                Vue.prototype.$error = function (msg) {
                    this.$msg({
                        status: false,
                        msg: msg,
                    });
                };
            
                /**
                 * @description 警告通知
                 * @param msg {string} 消息内容
                 * @param params {object} 配置参数
                 */
                Vue.prototype.$warning = function (msg) {
                    this.$msg({
                        icon: 0,
                        msg: msg,
                    });
                };
            
                Vue.component('bt-line', {
                    template: `<div class="line">
                        <span class="tname" :style="{'width':labelWidth}">{{label}}</span>
                        <div class="info-r" :style="{'margin-left':labelWidth}">
                            <slot></slot>
                        </div>
                    </div>`,
                    props: {
                        label: String,
                        labelWidth: String,
                    },
                });
            
                Vue.component('bt-text', {
                    template: `<div :class="{inlineBlock:!block,block:block,relative:iconInternal}" v-if="type === 'text' || type === 'number'">
                        <input type="text"
                        :type="type"
                        :id="id"
                        :value="value"
                        :class="custClass?custClass:('bt-input-text ' + (className || ''))"
                        :min="min"
                        :max="max"
                        :disabled="disabled"
                        :readonly="readonly"
                        :style="{width:width}"
                        :placeholder="placeholder" @input="$emit('input', $event.target.value)" @blur="$emit('blur',$event)" @keyup="$emit('keyup',$event)"/>
                        <span :class="'glyphicon glyphicon-'+ icon +' cursor'" v-if="icon" @click="$emit('icon-event')" :style="iconInternal?'':''"></span>
                        <span v-if="describe" class="unit">{{ describe }}</span>
                    </div>
                    <div class="inlineBlock" v-else-if="type === 'textarea'">
                        <textarea class="bt-input-text"
                            :style="{width:width,height:height,resize:resize?'auto':'',lineHeight:lineHeight}"
                            :disabled="disabled"
                            :readonly="readonly"
                            @input="$emit('input', $event.target.value)"
                            :value="value"
                            ref="text"
                            :placeholder="(tips && placeholder)"
                            @blur="hide_placeholder"
                            @click="show_placeholder"></textarea>
                        <div v-if="!tips" :class="'placeholder c9 '+  (value !== ''?'hide':'') " style="top:10px;left:15px;" v-html="(typeof placeholder == 'string'?placeholder:placeholder.join('</br>'))" v-show="textPlaceholder" @click.stop="show_placeholder"></div>
                    </div>`,
                    props: {
                        id: String,
                        type: {
                            type: String,
                            default: 'text',
                        },
                        width: {
                            type: String,
                            default: '200px',
                        },
                        resize: {
                            type: Boolean,
                            default: false,
                        },
                        height: {
                            type: String,
                            default: '100px',
                        },
                        custClass: {
                            type: String,
                            default: '',
                        },
                        block: {
                            type: false,
                            default: '',
                        },
                        iconInternal: {
                            type: Boolean,
                            default: false,
                        },
                        describe: {
                            type: String,
                            default: '',
                        },
                        lineHeight: String,
                        min: Number,
                        max: Number,
                        disabled: Boolean,
                        readonly: Boolean,
                        placeholder: [String, Array],
                        className: String,
                        icon: {
                            type: [String, Boolean],
                            default: false,
                        },
                        tips: {
                            type: Boolean,
                            default: false,
                        },
                        value: {
                            type: [String, Number],
                            default: '',
                        },
                    },
                    data() {
                        return {
                            textPlaceholder: true,
                            layerTips: 0,
                        };
                    },
                    watch: {
                        value: {
                            immediate: true,
                            handler(val) {
                                this.$emit('input', val);
                            },
                        },
                    },
                    methods: {
                        show_placeholder() {
                            let ps = this.placeholder;
                            if (typeof ps === 'string') ps = [ps];
                            this.textPlaceholder = false;
                            this.layerTips = layer.tips(ps.join('</br>'), this.$refs.text, {
                                tips: [1, '#20a53a'],
                                time: 0,
                                area: this.width,
                            });
                            this.$refs.text.focus();
                        },
                        hide_placeholder() {
                            this.textPlaceholder = true;
                            layer.close(this.layerTips);
                        },
                    },
                });
            
                Vue.component('bt-select', {
                    template: `
                  <div class="inlineBlock" ref="divSelect">
                    <div :class="'bt_select_updown mr10 '+ (disabled?'bt-disabled':'')" :style="{width:width}">
                        <span class="bt_select_value" style="padding-right: 20px;" @click="open_select_list">
                          <span class="bt_select_content">{{ content }}</span>
                          <span class="glyphicon glyphicon-triangle-bottom ml5"></span>
                        </span>
                        <ul ref="dropDown" class="bt_select_list" :class="{ show: showSelectList }" >
                          <slot></slot>
                        </ul>
                    </div>
                    <span v-if="describe" class="unit">{{ describe }}</span>
                  </div>
                `,
                    props: {
                        width: {
                            type: String,
                            default: '200px',
                        },
                        value: {
                            type: [String, Number, Boolean],
                            default: '',
                        },
                        disabled: {
                            type: Boolean,
                            default: false,
                        },
                        describe: {
                            type: String,
                            default: '',
                        }
                    },
                    data() {
                        return {
                            list: [],
                            content: '',
                            newValue: this.value,
                            showSelectList: false,
                        };
                    },
                    mounted() {
                        // this.get_select_title();
                        this.content = '';
                        this.list = this.get_option_list();
                        // 绑定事件
                        document.addEventListener('click', this.hide_select_list_event);
                    },
                    beforeDestroy() {
                        // 解除绑定事件
                        document.removeEventListener('click', this.hide_select_list_event);
                    },
                    methods: {
                        // 打开下拉列表
                        open_select_list() {
                            if (this.disabled) return false;
                            this.showSelectList = !this.showSelectList;
                        },
                        // 显示下拉列表
                        show_select_list() {
                            this.showSelectList = true;
                        },
                        // 隐藏下拉列表
                        hide_select_list() {
                            this.showSelectList = false;
                        },
                        // 隐藏下拉列表事件
                        hide_select_list_event(e) {
                            const { divSelect, dropDown } = this.$refs;
                            if (divSelect) {
                                if (!!divSelect.contains(e.target) || !!dropDown.contains(e.target)) {
                                    return;
                                } else {
                                    this.hide_select_list();
                                }
                            }
                        },
                        // 子组件选中数据
                        get_select_item(item) {
                            this.content = item.title;
                            this.newValue = item.value;
                            this.$children.forEach((vm, index) => {
                                vm.newValue = item.value;
                            });
                            this.hide_select_list();
                            this.$emit('input', this.newValue);
                            this.$emit('change', this.newValue);
                        },
                        // 获取配置列表信息
                        get_option_list() {
                            let list = [];
                            this.$children.forEach((vm, index) => {
                                if (vm.value === this.value) this.content = vm.title;
                                list.push({
                                    title: vm.title,
                                    value: vm.value,
                                });
                            });
                            if (this.value === '' && list.length > 0) {
                                this.get_select_item(list[0]);
                            }
                            return list;
                        },
                    },
                });
                Vue.component('bt-batch-select', {
                    template: `
                  <div class="inlineBlock" ref="divSelect">
                    <div :class="'bt_table_select_group mr10 '+ (disabled?'bt-disabled':'')">
                        <span class="bt_select_value" @click="open_select_list">
                          <span class="bt_select_content">{{ checkTitle }}</span>
                          <span class="glyphicon glyphicon-triangle-bottom ml5"></span>
                        </span>
                        <ul ref="dropDown" class="bt_selects" :class="{ show: showSelectList }" >
                          <slot></slot>
                        </ul>
                    </div>
                    <span v-if="describe" class="unit">{{ describe }}</span>
                  </div>
                `,
                    props: {
                        width: {
                            type: String,
                            default: '200px',
                        },
                        value: {
                            type: [String, Number, Boolean],
                            default: '',
                        },
                        disabled: {
                            type: Boolean,
                            default: false,
                        },
                        describe: {
                            type: String,
                            default: '',
                        },
                        checkNum: Number
                    },
                    data() {
                        return {
                            list: [],
                            newValue: this.value,
                            showSelectList: false,
                        };
                    },
                    mounted() {
                        this.list = this.get_option_list();
                        // 绑定事件
                        document.addEventListener('click', this.hide_select_list_event);
                    },
                    beforeDestroy() {
                        // 解除绑定事件
                        document.removeEventListener('click', this.hide_select_list_event);
                    },
                    methods: {
                        // 打开下拉列表
                        open_select_list() {
                            if (this.disabled) return false;
                            this.showSelectList = !this.showSelectList;
                        },
                        // 显示下拉列表
                        show_select_list() {
                            this.showSelectList = true;
                        },
                        // 隐藏下拉列表
                        hide_select_list() {
                            this.showSelectList = false;
                        },
                        // 隐藏下拉列表事件
                        hide_select_list_event(e) {
                            const { divSelect, dropDown } = this.$refs;
                            if (divSelect) {
                                if (!!divSelect.contains(e.target) || !!dropDown.contains(e.target)) {
                                    return;
                                } else {
                                    this.hide_select_list();
                                }
                            }
                        },
                        // 子组件选中数据
                        get_select_item(item) {
                            this.value = item.title+ ` (已选中${this.checkNum})`;
                            this.newValue = item.value;
                            this.$children.forEach((vm, index) => {
                                vm.newValue = item.value;
                            });
                            this.hide_select_list();
                            // this.$emit('input', this.newValue);
                            this.$emit('setevent', this.newValue);
                        },
                        // 获取配置列表信息
                        get_option_list() {
                            let list = [];
                            this.$children.forEach((vm, index) => {
                                list.push({
                                    title: vm.title,
                                    value: vm.value,
                                });
                            });
                            return list;
                        },
                    },
                    computed: {
                        checkTitle() {
                            return this.value
                        },
                    },
                });
            
                Vue.component('bt-option', {
                    template: `<li @click="select_down_item" :class="{'item':true,'active':value === newValue,'disabled':disabled}" :tips="tips">{{ title }}</li>`,
                    props: {
                        title: String,
                        value: [String, Boolean, Number],
                        tips: String,
                        disabled: Boolean,
                    },
                    data() {
                        return {
                            newValue: '',
                        };
                    },
                    methods: {
                        select_down_item() {
                            this.$parent.get_select_item({
                                title: this.title,
                                value: this.value,
                            });
                            // this.newValue =  this.$parent.newValue
                        },
                    },
                    mounted() {
                        this.newValue = this.$parent.newValue;
                    },
                });
            
                Vue.component('bt-radio', {
                    template: `<div class="inlineBlock"></div>`,
                });
            
                Vue.component('bt-switch', {
                    template: `<div class="inlineBlock">
                        <div class="mlr15">
                            <span class="alignMiddle">{{ label }}</span>
                            <div class="inlineBlock alignMiddle">
                                <input class="btswitch btswitch-ios hide" :id="random" type="checkbox" :checked="value" @change="input_event" :disabled="disabled">
                                <label :class="{'btswitch-btn':true,'disabled':disabled}" :for="random"></label>
                            </div>
                        </div>
                    </div>`,
                    props: {
                        label: String,
                        disabled: {
                            default: false,
                        },
                        value: {
                            type: Boolean,
                            default: false,
                        },
                    },
                    data() {
                        return {
                            random: 0,
                        };
                    },
                    mounted() {
                        this.random = bt.get_random(10);
                    },
                    methods: {
                        input_event: function (ev) {
                            this.$emit('input', ev.target.checked);
                            this.$emit('change', ev.target.checked);
                        },
                    },
                });
            
                Vue.component('bt-checkbox', {
                    template: `
                  <div class="inlineBlock">
                    <div :class="{'bt-checkbox':true,disabled:disabled}">
                      <label :class="{cursor:!disabled}" style="font-weight: 500;">
                        <span :class="{mr5:label}">
                          <i :class="{'cust—checkbox':true,'cursor-pointer':true,'active':parseInt(value)}" style="vertical-align: sub;" @click="onShowTips($event)"></i>
                          <input type="checkbox" :checked="parseInt(value)" :value="value" class="hide" @input="input_event" :disabled="disabled"/>
                        </span>
                        <span v-if="label">{{ label }}</span>
                      </label>
                    </div>
                  </div>
                `,
                    props: {
                        label: {
                            type: String,
                            value: '',
                        },
                        value: {
                            type: [Boolean, Number],
                            default: 0,
                        },
                        disabled: {
                            type: Boolean,
                            default: false,
                        },
                        tips: {
                            type: String,
                            default: '',
                        },
                        showTips: {
                            type: Boolean,
                            default: false,
                        },
                    },
                    methods: {
                        onShowTips: function (e) {
                            const tips = this.tips;
                            const showTips = this.showTips;
                            const disabled = this.disabled;
                            if (!showTips || !disabled || !tips) return;
                            layer.tips(tips, $(e.target), {
                                tips: [1, 'red'],
                                time: 3000,
                                success($layer) {
                                    let left = parseFloat($layer.css('left'));
                                    left -= 10;
                                    $layer.css('left', `${left}px`);
                                },
                            });
                        },
                        input_event: function (ev) {
                            this.$emit('input', ev.target.checked ? 1 : 0);
                            this.$emit('change', ev.target.checked);
                        },
                    },
                });
            
                Vue.component('bt-button', {
                    template: `<div class="inlineBlock"><button type="text" :class="'btn btn-'+ size +' btn-' + type +' '+ className" @click="$emit('click', $event);" :disabled="disabled">{{ title }}</button></div>`,
                    props: {
                        size: {
                            type: String,
                            default: 'sm',
                        },
                        title: {
                            type: String,
                            default: '按钮',
                        },
                        type: {
                            type: String,
                            default: 'default',
                        },
                        className: {
                            type: String,
                            default: '',
                        },
                        disabled: {
                            type: Boolean,
                            default: false,
                        },
                    },
                });
            
                Vue.component('bt-help', {
                    template: `<ul class="help-info-text c7" style="padding:0 30px 0 30px">
                        <li v-for="(item,index) in list" :key="index" :style="{'color':(item[1] || '#777')}">{{ item[0] }}</li>
                    </ul>`,
                    props: {
                        list: {
                            type: Array,
                            default() {
                                return [];
                            },
                        },
                    },
                });
            
                Vue.component('bt-link', {
                    template: `<div class="inlineBlock">\
																	<a :href="href" :class="{'bt_success':status,'bt_danger':!status,'bt_warning':status === 2}" @click="$emit('click')" :target="target" :title="tips || title">
																	<span>{{ title }}</span>
																	<span :class="'glyphicon glyphicon-' + icon " v-if="icon"></span>
																	</a>
                              </div>`,
                    props: {
                        tips: String,
                        icon: {
                            type: [String, Boolean],
                            default: false,
                        },
                        status: {
                            type: [Boolean, Number],
                            default: true,
                        },
                        href: {
                            type: String,
                            default: 'javascript:void(0);',
                        },
                        target: {
                            type: [String, Boolean],
                            default: false,
                        },
                        title: String,
                    }
                });
            
                Vue.component('bt-link-group', {
                    template: `<span class="bt-link-group"><slot></slot></span>`,
                });
            
                Vue.component('bt-tabs', {
                    template: `<div class="bt-tabs">
                        <div class="bt-w-menu site-menu pull-left" style="height: 100%;">
                            <p v-for="(item,index) in tabList" :class="{...{bgw:value === item.name},...className}" @click="cut_tabs(item,data)">{{item.label}}</p>
                        </div>
                        <div class="bt-w-con">
                           <slot></slot>
                        </div>
                    </div>`,
                    props: {
                        value: {
                            type: String,
                            default: 'default',
                        },
                        className: {
                            type: Object,
                            default() {
                                return {};
                            },
                        },
                        data: Object,
                        tabRefresh: {
                            type: Boolean,
                            default: false,
                        },
                    },
                    data() {
                        return {
                            model: this.value,
                            tabList: [],
                            publicView: false,
                        };
                    },
                    watch: {
                        value: {
                            immediate: true,
                            handler(val) {
                                this.cut_tabs(
                                    {
                                        name: val,
                                    },
                                    this.data,
                                    true
                                );
                            },
                        },
                    },
                    mounted() {
                        this.tabList = this.getTabList();
                    },
                    methods: {
                        // 获取Tab列表
                        getTabList() {
                            let list = [];
                            this.$children.forEach((vm, index) => {
                                list.push(
                                    Object.assign({}, vm.$attrs, {
                                        name: vm.name,
                                    })
                                );
                                if (vm.public) this.publicView = true;
                            });
                            return list;
                        },
                        cut_tabs(item, row, type) {
                            this.$children.forEach((vm, index) => {
                                if (vm.name === item.name && vm.refresh) {
                                    vm.tabsRefresh = false;
                                    this.$nextTick(() => {
                                        vm.tabsRefresh = true;
                                    });
                                }
                                vm.model = item.name;
                            });
                            if (typeof type === 'undefined') {
                                this.$emit('input', item.name);
                                this.$emit('change', item, row);
                            }
                        },
                    },
                });
            
                Vue.component('bt-tabs-pane', {
                    template: `<div class="bt-tabs-item pd15" style="overflow: auto;" v-if="model === name && tabsRefresh || public">
                                                            <template v-if="public">
                                                                            <slot></slot>
                                                            </template>
                        <template v-else-if="component && !keepAlive">
                            <component :is="component" :data="data"></component>
                        </template>
                        <template v-else-if="keepAlive && component">
                            <keep-alive>
                                <component :is="component" :data="data"></component>
                            </keep-alive>
                        </template>
                        <template v-else-if="!isSlot">
                            <div id="webedit-con" style="height: 100%;"></div>
                        </template>
                        <template v-else>
                            <slot></slot>
                        </template>
                    </div>`,
                    props: {
                        name: String,
                        component: String,
                        public: {
                            type: Boolean,
                            default: false,
                        },
                        keepAlive: {
                            type: Boolean,
                            default: true,
                        },
                        config: Object,
                        refresh: {
                            type: Boolean,
                            default: false,
                        },
                    },
                    data() {
                        return {
                            model: '',
                            data: '',
                            isSlot: '',
                            tabsRefresh: true,
                            publicView: false,
                        };
                    },
                    mounted() {
                        if (typeof this.$slots.default != 'undefined') this.isSlot = true;
                        this.data = this.$parent.data;
                        this.model = this.$parent.model;
                        this.publicView = this.$parent.publicView;
                    },
                });
            
                Vue.component('bt-table-page', {
                    template: `<div class="page">
                                                            <template v-if="value !== 1">
                                        <a class="Pnum" @click="cut_page_event(1)">首页</a>
                                        <a class="Pnum" @click="cut_page_event(value - 1)">上一页</a>
                                                            </template>
                        <template v-for="(item,index) in pageNumber">
                            <span class="Pcurrent" v-if="item === value">{{item}}</span>
                            <a class="Pnum" @click="cut_page_event(item)" v-else>{{item}}</a>
                        </template>
                        <template v-if="pageNumber !== value && pageNumber != 0">
                            <a class="Pnum" @click="cut_page_event(value + 1)">下一页</a>
                                        <a class="Pnum" @click="cut_page_event(pageNumber)" >尾页</a>
                                                            </template>
            
                        <span class="Pcount">共{{ pageTotal }}条</span>
            <!--            <select class="page_select_number" v-model="pageLimit">-->
            <!--                <option v-for="(item,index) in pageList" :key="index" :value="item">{{ item }}条/页</option>-->
            <!--            </select>-->
            <!--            <div class="page_jump_group">-->
            <!--                <span class="page_jump_title">跳转到</span>-->
            <!--                <input type="number" class="page_jump_input" v-model="value" @keyup.enter="cut_page_event">-->
            <!--                <span class="page_jump_title">页</span>-->
            <!--                <button type="button" class="page_jump_btn" @click="cut_page_event">确认</button>-->
            <!--            </div>-->
                    </div>`,
                    props: {
                        // 分页数
                        value: Number,
            
                        // 全部数量
                        pageTotal: {
                            type: Number,
                            default: 0,
                        },
                        // 每页页数限制
                        pageLimit: Number,
                    },
                    data() {
                        return {
                            pageList: [10, 20, 50, 100, 200],
                        };
                    },
                    computed: {
                        pageNumber() {
                            return Math.ceil(this.pageTotal / this.pageLimit);
                        },
                    },
                    methods: {
                        // 切换分页事件
                        cut_page_event(page) {
                            page = parseInt(page);
                            this.$emit('cut-page', page);
                            this.$emit('input', page);
                        },
                    },
                    mounted() {},
                });
            
                Vue.component('bt-table', {
                    template: `
                  <div>
                    <div class="bt-table">
                      <div class="divtable mtb10">
                        <table class="table table-hover" :style="{minWidth:minWidth,maxWidth:maxWidth}">
                          <thead>
                            <tr>
                              <th v-for="(item,index) in theadList" :style="{textAlign:item.align,width:item.width,minWidth:item.minWidth,maxWidth:item.maxWidth}">
                                <bt-checkbox v-model="checkboxAll" v-if="item.type === 'checkbox'" @change="set_checked"></bt-checkbox>
                                <span v-else>{{item.title}}</span>
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            <bt-column v-for="(item,index) in newData" :key="item[dataKey] || index" :row="item" :index="index"><slot></slot></bt-column>
                            <tr v-if="newData.length === 0"><td :colspan="theadList.length" style="text-align: center">列表数据为空</td></tr>
                          </tbody>
                        </table>
                        <div class="hide"><slot></slot></div>
                      </div>
                    </div>
                    <div class="tootls_group clearfix" v-if="batch || page">
                      <div class="pull-left" style="line-height: 28px;" v-if="batch">
                        <bt-checkbox v-model="checkboxAll" @change="set_checked" style="padding: 0 9px"></bt-checkbox>
                        <template v-if="batchList.length == 1">
                          <div class="bt_batch inlineBlock">
                            <button
                              class="btn btn-default btn-sm"
                              :class="{ 'bt-disabled': checkboxList.length < 1, 'btn-success': checkboxList.length >= 1 }"
                              style="margin-left: 2px;"
                              @click="onSingleBatchClick($event)">{{ batchList[0].title + checkTitle }}</button>
                          </div>
                        </template>
                        <template v-else-if="batchList.length > 1">
                          <bt-batch-select v-model="batchVal" :disabled="checkboxList.length < 1" width="150px" class="bt_batch" :checkNum="checkboxList.length" @setevent="onBatchEvent">
                            <bt-option v-for="(item,index) in batchList" :key="index" :title="item.title" :value="item.value"></bt-option>
                          </bt-batch-select>
                          <bt-button :type="checkboxList.length < 1?'default':'success'" title="批量操作" :disabled="checkboxList.length < 1" @click="onBatchClick"></bt-button>
                        </template>
                      </div>
                      <div class="pull-right" v-if="typeof page == 'number'">
                        <bt-table-page v-model="page" :page-total="pageTotal" :page-limit="pageLimit" @cut-page="cutPageNumber"></bt-table-page>
                      </div>
                    </div>
                  </div>
                `,
                    props: {
                        dataKey: String,
                        minWidth: String,
                        maxWidth: String,
                        fixedHead: {
                            type: Boolean,
                            default: true,
                        },
                        data: {
                            type: [Object, Array],
                            default: function () {
                                return {};
                            },
                        },
                        batch: {
                            type: Boolean,
                            default: false,
                        },
                        batchList: Array,
                        page: Number,
                        pageTotal: {
                            type: Number,
                            default: 0,
                        },
                        pageLimit: {
                            type: Number,
                            default: 10,
                        },
                    },
                    data: function () {
                        return {
                            theadList: [],
                            newData: [],
                            theadListlength: 0,
                            checkboxAll: 0,
                            checkboxList: [],
                            batchVal: '',
                            batchApi:''
                        };
                    },
                    computed: {
                        checkTitle() {
                            return this.checkboxList.length > 0
                                ? `(已选中${this.checkboxList.length})`
                                : '';
                        },
                    },
                    watch: {
                        data: {
                            immediate: true,
                            handler(val) {
                                this.newData = [];
                                this.$nextTick(() => {
                                    this.newData = this.data;
                                });
                            },
                        },
                    },
                    mounted() {
                        this.newData = this.data;
                        this.checkboxList = [];
                        this.set_checked();
                        this.get_col_list();
                    },
                    methods: {
                        clear_batch_val(){
                            this.checkboxList = [];
                            this.checkboxAll = 0;
                            this.batchVal = `请选择批量操作`
                            this.batchApi = ''
														$($(this.$el)[0]).find('.bt_selects li').removeClass('active')
                        },
                        set_checked(val) {
                            this.newData.forEach((v, index) => {
                                this.$set(v, 'isChecked', val ? 1 : 0);
                                this.checkboxList.push(index);
                                this.checkboxList = Array.from(new Set(this.checkboxList))  //去重
                            });
                            if (!val){
                                this.batchVal = `请选择批量操作`
                                this.checkboxList = [];
                            }else{
                                this.batchVal = `请选择批量操作 (已选中${this.checkboxList.length})`
                            }
                            if (this.data.length <= 0) {
                                this.checkboxAll = 0;
                            }
                        },
                        reset_checked() {
                            this.checkboxList = [];
                            this.checkboxAll = 0;
                        },
                        /**
                         * @description 获取表格列数
                         */
                        get_col_list() {
                            this.theadListlength = this.$children.length;
                            this.$children.forEach((vm, index) => {
                                if (typeof vm.isThead === 'undefined') return true;
                                this.theadList.push({
                                    title: vm.title,
                                    type: vm.type || 'default',
                                    align: vm.align,
                                    width: vm.width,
                                    name: vm.name,
                                    maxWidth: vm.maxWidth,
                                    minWidth: vm.minWidth,
                                });
                                if (index === this.theadListlength) return false;
                            });
                        },
                        /**
                         * @description 切换分页数
                         * @param {number} page 分页
                         */
                        cutPageNumber(page) {
                            this.$emit('cut-pages', page);
                        },
                        onBatchClick (e) {
                            const that = this;
                            const val = this.batchApi;
                            const list = [];
                            const checkSite = {check_list:[]}
                            this.checkboxList.forEach((v, index) => {
                                list.push(this.newData[v]['name'])
                                checkSite['check_list'].push(this.newData[v])
                            });
                            // this.$emit('onBatch', val, list);
                            const address = $(e.target).parents('.pull-left').find('.bt_batch')
                            if(val == ''){
                                layer.tips('请选择需要批量操作的类型', address, {
                                    tips: [1, 'red'],
                                    time: 2000
                                });
                            }
                            let _api = val,param = {},apiHead = {},_title = '',_content = ''
                            switch (val){
                                case 'multi_open_project':   //打开
                                case 'multi_close_project':  //关闭
                                    _api = 'multi_set_project'
                                    param['operation'] = val == 'multi_open_project' ? 'start' : 'stop'
                                    _title = val == 'multi_open_project' ? '批量开启项目' : '批量停用项目'
                                    _content = val == 'multi_open_project' ? '批量启用选中的项目后，项目将恢复正常访问，是否继续操作？' : '批量停用选中的项目后，项目将无法正常访问，用户访问会显示当前项目停用页面，是否继续操作？'
                                case 'multi_check_bind_extranet':  //绑定外网
                                    _title = val == 'multi_check_bind_extranet'?'批量绑定外网':_title
                                    _content = val == 'multi_check_bind_extranet'?'批量绑定选中的项目后，项目将可以通过外网访问，是否继续操作？':_content
            
                                    //设置参数
                                    apiHead[_api] = val == 'multi_check_bind_extranet' ? '批量绑定外网' : (val == 'multi_open_project' ? '批量开启项目' : '批量停用项目')
                                    param['project_names'] = list
            
                                    bt.simple_confirm({title:_title,msg:_content}, async function(layers) {
                                        layer.close(layers)
                                        let rdata = await that.$http(apiHead,param);
                                        showBatchResultTable(rdata)
                                    })
                                    break;
                                case 'multi_remove_project':   //删除
                                    _title = '批量删除项目'
                                    _content = '批量删除选中的项目后，项目将无法恢复，是否继续操作？'
                                    bt.prompt_confirm(_title, _content, async function () {
                                        let rdata = await that.$http({multi_remove_project:'批量删除项目'},{project_names:list});
                                        showBatchResultTable(rdata)
                                    })
                                    break;
                                case 'multi_setup_ssl':   //绑定证书
                                    site.set_ssl_cert(checkSite)
                                    break;
                            }
                            // 展示批量操作结果
                            function showBatchResultTable(result){
                                let html = '';
                                $.each(result.error_list, function (key, item) {
                                    html += '<tr><td><span class="text-overflow" title="' + item.project_name + '">' + item.project_name + '</span/></td><td><div style="float:right;white-space: initial;" class="size_ellipsis"><span style="color:red">' + item.msg + '</span></div></td></tr>';
                                });
                                $.each(result.project_names, function (index, item) {
                                    html += '<tr><td><span class="text-overflow" title="' + item + '">' + item + '</span></td><td><div style="float:right;" class="size_ellipsis"><span style="color:#20a53a">操作成功</span></div></td></tr>';
                                });
                                bt_tools.$batch_success_table({ title: _title, th: '项目名称', html: html });
                                javaModle.get_project_list()
                                that.clear_batch_val()
                            }
                        },
                        onSingleBatchClick(e) {
                            const list = this.checkboxList;
                            if (list.length > 0) {
                                this.$emit('onSingleBatch', list);
                            } else {
                                layer.tips('请选择需要批量操作的数据', $(e.target), {
                                    tips: [1, 'red'],
                                    time: 2000,
                                });
                            }
                        },
                        onBatchEvent(e){
                            this.batchApi = e
                        }
                    },
                });
            
                Vue.component('bt-column', {
                    template: `<tr><slot></slot></tr>`,
                    props: {
                        row: {
                            type: Object,
                            default() {
                                return {};
                            },
                        },
                        index: Number,
                        label: String,
                    },
                    watch: {
                        row: {
                            immediate: true,
                            handler(val) {
                                this.$children.row = this.row;
                            },
                        },
                    },
                    mounted() {},
                });
            
                Vue.component('bt-table-column', {
                    template: `<td v-if="isThead">
                            <span :style="{width:fixedWidth && width?width:false,textAlign:align}" :class="{size_ellipsis:fixedWidth}" >
                                <template v-if="type === 'checkbox'">
                                    <bt-checkbox v-model="row.isChecked" @change="checkbox_change" ref="checkbox"></bt-checkbox>
                                </template>
                                <template v-else-if="prop">{{ row[prop] }}</template>
                                <template v-else><slot :$row="row" :$index="index"></slot></template>
                            </span>
                        </td>`,
                    props: {
                        scope: {
                            type: [Object, Array, Boolean],
                            default: false,
                        },
                        type: {
                            type: String,
                            default: 'default',
                        },
                        title: [String, Number],
                        width: String,
                        maxWidth: String,
                        minWidth: String,
                        prop: String,
                        align: String,
                        fixedWidth: Boolean,
                    },
                    data() {
                        return {
                            isThead: false,
                            row: {},
                            label: null,
                            index: -1,
                        };
                    },
                    methods: {
                        checkbox_change: function (value) {
                            let location = this.$parent.$parent.checkboxList.indexOf(
                                this.$parent.index
                            );
                            if (!value) {
                                this.$parent.$parent.checkboxAll = 0;
                                this.$parent.$parent.checkboxList.splice(location, 1);
                            } else {
                                this.$parent.$parent.checkboxList.push(this.$parent.index);
                                if (
                                    this.$parent.$parent.newData.length ===
                                    this.$parent.$parent.checkboxList.length
                                ) {
                                    this.$parent.$parent.checkboxAll = 1;
                                }
                            }
                            this.$parent.$parent.batchVal = `请选择批量操作${this.$parent.$parent.checkboxList.length > 0 ? ` (已选中`+this.$parent.$parent.checkboxList.length+`)` : ''}`;
                        },
                    },
                    mounted() {
                        if (this.$isType(this.$parent.row) === 'object') {
                            this.isThead = true;
                            this.label = this.$parent.label;
                            this.row = this.$parent.row;
                            this.index = this.$parent.index;
                        }
                    },
                });
            
                Vue.component('bt-layer', {
                    template: `<div :id="random" :class="((className?(className + ' bt-layer-view'):'')  || {pd30:true,pb70:!btn,'bt-layer-view':true})" v-if="this.status" v-cloak>
                    <slot></slot>
                </div>`,
                    props: {
                        title: {
                            type: String,
                            default: '默认标题',
                        },
                        value: {
                            type: [Number, Boolean],
                            default: false,
                        },
                        area: {
                            type: [String, Array],
                            default: '400px',
                        },
                        btn: Array,
                        className: {
                            type: [String, Object],
                            default: '',
                        },
                    },
                    data() {
                        return {
                            random: null,
                            status: this.value,
                            view: null,
                        };
                    },
                    watch: {
                        value(newValue) {
                            !newValue ? this.close() : this.create();
                        },
                    },
                    mounted() {
                        this.random = bt.get_random(10);
                    },
                    methods: {
                        // 关闭视图
                        close() {
                            layer.close(this.view);
                        },
                        // 视图创建的回调
                        create() {
                            let area = [];
                            this.status = true;
                            this.$nextTick(() => {
                                layer.open({
                                    type: 1,
                                    title: this.title || false,
                                    area: this.area,
                                    btn: false,
                                    closeBtn: this.closeBtn || 2,
                                    content: $(`#${this.random}`),
                                    success: (layer, index) => {
                                        this.$emit('success');
                                        this.view = index;
                                    },
                                    end: () => {
                                        this.$emit('close');
                                        this.status = false;
                                        this.$emit('input', this.status);
                                    },
                                });
                            });
                        },
                    },
                });
            
                // 网站管理-通用模块-日志组件
                Vue.component('bt-site-logs', {
                    template: `<pre class="command_output_pre" style="height:640px;" ref="command" >{{command}}</pre>`,
                    props: {
                        data: Object,
                    },
                    data: function () {
                        return {
                            command: '',
                            path: '',
                            size: '',
                            rdata: {},
                            html: '',
                            configInfo: {},
                        };
                    },
                    mounted: function () {
                        this.get_project_logs();
                    },
                    methods: {
                        async onEnter() {
                            layer.tips('当日志文件过大时，读取和搜索时间会增加，同时也会占用存储空间，因此需要对日志进行切割以方便管理和维护。', this.$el.querySelector('.log-split'), {tips: [3, '#20a53a'], time: 0});
                        },
                        async onLeave() {
                            layer.closeAll('tips');
                        },
                        async get_project_logs() {
                            try {
                                let rdata = await this.$http(
                                    {
                                        get_project_log: '获取项目日志',
                                        verify: false,
                                    },
                                    {
                                        project_name: this.data.name,
                                    }
                                );
                                this.command = rdata.msg;
                                // this.path = rdata.path;
                                // this.size = rdata.size;
                                // this.get_log_split();
                                this.$nextTick(() => {
                                    this.$refs.command.scrollTop = this.$refs.command.scrollHeight;
                                });
                            } catch (e) {
                                this.$msg(e);
                            }
                        },
                        async get_log_split() {
                            try {
                                let rdata = await this.$http({
                                    get_log_split: '获取日志切割',
                                    verify: false,
                                },{
                                    name: this.data.name,
                                });
                                this.rdata = rdata;
                                if(rdata.status) {
                                    this.configInfo = rdata.data;
                                }
                                this.html = '开启后' + (rdata.status ? rdata.data.log_size ? '日志文件大小超过'+ bt.format_size(rdata.data.log_size,true,2,'MB') +'时进行切割日志文件' : '每天'+ rdata.data.hour +'点' + rdata.data.minute + '分进行切割日志文件' : '默认每天2点0分进行切割日志文件')
                            } catch (e) {
                                this.$msg(e);
                            }
                        },
                        async set_log_split() {
                            let that = this;
                            bt.confirm(
                                {
                                    title: '设置日志切割任务',
                                    msg: !this.rdata.status || (this.rdata.status && !this.rdata.data.status) ? '开启后对该项目日志进行切割，是否继续操作？' : '关闭后将无法对该项目日志进行切割，是否继续操作？',
                                },
                                async () => {
                                    try {
                                        if(that.rdata.status){
                                            res = await that.$http({
                                                set_log_split: '设置日志切割任务',
                                            },{
                                                name: that.data.name,
                                            });
                                        }else{
                                            res = await that.$http({
                                                mamger_log_split: '设置日志切割任务',
                                                verify: false,
                                            },{
                                                name: that.data.name,
                                            });
                                        }
                                        that.$msg(res);
                                        if(res.status) {
                                            that.get_project_logs();
                                        }
                                    } catch (e) {
                                        this.$msg(e);
                                    }
                                }
                            );
                        },
                        async mamger_log_split () {
                            let that = this;
                            var configInfo = this.configInfo;
                            bt_tools.open({
                                type: 1,
                                area: '460px',
                                title: '配置日志切割任务',
                                closeBtn: 2,
                                btn: ['提交', '取消'],
                                content: {
                                    'class': 'pd20 mamger_log_split_box',
                                    form: [{
                                        label: '执行时间',
                                        group: [{
                                            type: 'text',
                                            name: 'day',
                                            width: '44px',
                                            value: '每天',
                                            disabled: true
                                        },{
                                            type: 'number',
                                            name: 'hour',
                                            'class': 'group',
                                            width: '70px',
                                            value: configInfo.hour || '2',
                                            unit: '时',
                                            min: 0,
                                            max: 23
                                        }, {
                                            type: 'number',
                                            name: 'minute',
                                            'class': 'group',
                                            width: '70px',
                                            min: 0,
                                            max: 59,
                                            value: configInfo.minute || '0',
                                            unit: '分'
                                        }]
                                    },{
                                        label: '日志大小',
                                        group:{
                                            type: 'text',
                                            name: 'log_size',
                                            width: '220px',
                                            value: configInfo.log_size ? bt.format_size(configInfo.log_size,true,2,'MB').replace(' MB','') : '',
                                            unit: 'MB',
                                            placeholder: '请输入日志大小',
                                        }
                                    }, {
                                        label: '保留最新',
                                        group:{
                                            type: 'number',
                                            name: 'num',
                                            'class': 'group',
                                            width: '70px',
                                            value: configInfo.num || '180',
                                            unit: '份'
                                        }
                                    }]
                                },
                                success: function (layero, index) {
                                    $(layero).find('.mamger_log_split_box .bt-form').prepend('<div class="line">\
                                                                                                            <span class="tname">切割方式</span>\
                                                                                                            <div class="info-r">\
                                                                                                                            <div class="replace_content_view" style="line-height: 32px;">\
                                                                                                                                            <div class="checkbox_config">\
                                                                                                                                                            <i class="file_find_radio '+ (configInfo.log_size ? 'active' : '') +'"></i>\
                                                                                                                                                            <span class="laberText" style="font-size: 12px;">按日志大小</span>\
                                                                                                                                            </div>\
                                                                                                                                            <div class="checkbox_config">\
                                                                                                                                                            <i class="file_find_radio '+ (configInfo.log_size ? '' : 'active') +'"></i>\
                                                                                                                                                            <span class="laberText" style="font-size: 12px;">按执行周期</span>\
                                                                                                                                            </div>\
                                                                                                                            </div>\
                                                                                                            </div>')
                                    $(layero).find('.mamger_log_split_box .bt-form').append('<div class="line"><div class=""><div class="inlineBlock  "><ul class="help-info-text c7"><li>每5分钟执行一次</li><li>【日志大小】：日志文件大小超过指定大小时进行切割日志文件</li><li>【保留最新】：保留最新的日志文件，超过指定数量时，将自动删除旧的日志文件</li></ul></div></div></div>')
                                    $(layero).find('.replace_content_view .checkbox_config').click(function(){
                                        var index = $(this).index()
                                        $(this).find('i').addClass('active').parent().siblings().find('i').removeClass('active')
                                        if(index){
                                            $(layero).find('[name=hour]').parent().parent().parent().show()
                                            $(layero).find('[name=log_size]').parent().parent().parent().hide()
                                            $(layero).find('.help-info-text li').eq(0).hide().next().hide()
                                        }else{
                                            $(layero).find('[name=hour]').parent().parent().parent().hide()
                                            $(layero).find('[name=log_size]').parent().parent().parent().show()
                                            $(layero).find('.help-info-text li').eq(0).show().next().show()
                                        }
                                    })
                                    if(configInfo.log_size) {
                                        $(layero).find('[name=hour]').parent().parent().parent().hide()
                                    }else{
                                        $(layero).find('[name=log_size]').parent().parent().parent().hide()
                                        $(layero).find('.help-info-text li').eq(0).hide().next().hide()
                                    }
                                    $(layero).find('[name=log_size]').on('input', function(){
                                        if($(this).val() < 1 || !bt.isInteger(parseFloat($(this).val()))) {
                                            layer.tips('请输入日志大小大于0的的整数', $(this), { tips: [1, 'red'], time: 2000 })
                                        }
                                    })
                                    $(layero).find('[name=hour]').on('input', function(){
                                        if($(this).val() > 23 || $(this).val() < 0 || !bt.isInteger(parseFloat($(this).val()))) {
                                            layer.tips('请输入小时范围0-23的整数时', $(this), { tips: [1, 'red'], time: 2000 })
                                        }
                                        $(layero).find('.hour').text($(this).val())
                                    })
                                    $(layero).find('[name=minute]').on('input', function(){
                                        if($(this).val() > 59 || $(this).val() < 0 || !bt.isInteger(parseFloat($(this).val()))) {
                                            layer.tips('请输入正确分钟范围0-59分的整数', $(this), { tips: [1, 'red'], time: 2000 })
                                        }
                                        $(layero).find('.minute').text($(this).val())
                                    })
                                    $(layero).find('[name=num]').on('input', function(){
                                        if($(this).val() < 1 || $(this).val() > 1800 || !bt.isInteger(parseFloat($(this).val()))) {
                                            layer.tips('请输入保留最新范围1-1800的整数', $(this), { tips: [1, 'red'], time: 2000 })
                                        }
                                    })
                                },
                                yes: async function (formD,indexs) {
                                    formD['name'] = that.data.name
                                    delete formD['day']
                                    if($('.mamger_log_split_box .file_find_radio.active').parent().index()) {
                                        if (formD.hour < 0 || formD.hour > 23 || isNaN(formD.hour) || formD.hour === '' || !bt.isInteger(parseFloat(formD.hour))) return layer.msg('请输入小时范围0-23时的整数')
                                        if (formD.minute < 0 || formD.minute > 59 || isNaN(formD.minute) || formD.minute === '' || !bt.isInteger(parseFloat(formD.minute))) return layer.msg('请输入正确分钟范围0-59分的整数')
                                        formD['log_size'] = 0
                                    }else{
                                        if(formD.log_size == '' || !bt.isInteger(parseFloat(formD.log_size))) return layer.msg('请输入日志大小大于0的的整数')
                                    }
                                    if(formD.num < 1 || formD.num > 1800 || !bt.isInteger(parseFloat(formD.num))) return layer.msg('请输入保留最新范围1-1800的整数')
                                    if(!that.rdata.status || (that.rdata.status && !that.rdata.data.status)) {
                                        if(that.rdata.status){
                                            let res = await that.$http({
                                                set_log_split: '设置日志切割任务',
                                            },{
                                                name: that.data.name,
                                            });
                                            if(res.status) pub_open()
                                        }else{
                                            pub_open()
                                        }
                                    }else{
                                        pub_open()
                                    }
                                    async function pub_open() {
                                        let res = await that.$http({
                                            mamger_log_split: '设置日志切割任务',
                                            verify: false,
                                        },formD);
                                        that.$msg(res);
                                        layer.close(indexs)
                                        if(res.status) {
                                            that.get_project_logs();
                                        }
                                    }
                                }
                            })
                        }
                    },
                });
            
                // 网站管理-通用模块-外网映射
                Vue.component('bt-site-network-mapping', {
                    template: `<div class="ptb15">
                        <bt-switch label="外网映射" v-model="bind_extranet" @change="set_bind_extranet" :disabled="disabled"></bt-switch>
                        <bt-help :list="help_list"></bt-help>
                    </div>`,
                    props: {
                        data: Object,
                    },
                    data: function () {
                        return {
                            project_type: 0,
                            disabled: false,
                            help_list: [
                                ['如果您的是HTTP项目，且需要外网通过80/443访问，请开启外网映射'],
                                ['开启外网映射前，请到【域名管理】中至少添加1个域名'],
                            ],
                            bind_extranet: !!this.data.project_config.bind_extranet,
                        };
                    },
                    methods: {
                        // 设置外网映射
                        async set_bind_extranet(value) {
                            let param = {};
                            param[value ? 'bind_extranet' : 'unbind_extranet'] = value
                                ? '开启外网映射'
                                : '关闭外网映射';
                            param['verify'] = false;
                            try {
                                let rdata = await this.$http(param, {
                                    project_name: this.data.name,
                                });
                                if (rdata.status) {
                                    this.$parent.data = await this.$root.get_project_info(
                                        this.data.name
                                    );
                                    this.$root.projectInfo = this.$parent.data;
                                    this.$parent.data.project_config.bind_extranet = value ? 1 : 0;
                                } else {
                                    this.bind_extranet = !value;
                                    this.$parent.data.project_config.bind_extranet = !value;
                                }
                                this.$msg(rdata);
                            } catch (e) {}
                        },
                        // 设置禁用
                        set_disable() {
                            switch (this.$request) {
                                case 'java':
                                    if (this.project_type < 3) return true;
                                    break;
                            }
                            return false;
                        },
                    },
                    mounted() {
                        let config = this.data.project_config;
                        switch (config.java_type) {
                            case 'springboot':
                                this.project_type = 3;
                                break;
                            case 'duli':
                                this.project_type = 2;
                                break;
                            case 'neizhi':
                                this.project_type = 1;
                                break;
                        }
                        this.disabled = this.set_disable();
                        if (this.$request === 'java' && this.project_type < 3)
                            this.help_list.push([
                                'JAVA项目类型为内置项目和独立项目时无法关闭外网映射',
                                'red',
                            ]);
                    },
                });
            
                // 网站管理-通用模块-域名管理
                Vue.component('bt-site-domain', {
                    template: `<div class="block">
                        <div class="line relative">
                            <bt-text class="relative" type="textarea" width="380px" height="120px"
                                     v-model="domainInfo"
                                     line-height="20px"
                                     :placeholder="['如果需要绑定外网，请输入需要绑定的域名，该选项可为空','如需填写多个域名，请换行填写，每行一个域名，默认为80端口','泛解析添加方法 *.domain.com', '暂不支持添加端口格式的域名 *.domain.com:88']"/>
                            <bt-button type="success" title="添加" @click="add_domain_info" style="position: absolute;right: 30px;top:35px"></bt-button>
                        </div>
                        <bt-table ref="domainTable" data-key="id" :data="domainList" :batch="true" :batchList="batchList" @onSingleBatch="onBatchDel">
                            <bt-table-column type="checkbox" width="20px"></bt-table-column>
                            <bt-table-column title="域名" v-slot="scope">
                                <bt-link :title="scope.$row.name" :href="'http://'+ scope.$row.name + ':' + scope.$row.port" target="_blank"></bt-link>
                            </bt-table-column>
                            <bt-table-column title="端口" width="100px" prop="port"></bt-table-column>
                            <bt-table-column title="操作" width="80px" align="right" v-slot="scope">
                                <bt-link title="删除" @click="del_domain_info(scope.$row,scope.$index)" v-if="set_disable(scope.$row)"></bt-link>
                                <span v-else>不可操作</span>
                            </bt-table-column>
                        </bt-table>
                    </div>`,
                    props: {
                        data: Object,
                    },
                    data: function () {
                        return {
                            disabled: false,
                            project_type: 0,
                            domainInfo: '',
                            domainList: [],
                            batchList: [
                                {
                                    title: '批量删除',
                                },
                            ],
                        };
                    },
                    methods: {
                        // 获取域名列表
                        async get_domain_list() {
                            try {
                                this.domainList = await this.$http(
                                    {
                                        project_get_domain: '获取项目域名列表',
                                    },
                                    {
                                        project_name: this.data.name,
                                    }
                                );
                            } catch (e) {
                                this.$msg(e);
                            }
                        },
                        // 添加域名信息
                        async add_domain_info() {
                            if (this.domainInfo === '') {
                                this.$error('域名不能为空');
                                return false;
                            }
                            let domainList = bt.check_domain_list(this.domainInfo);
                            if (!domainList) return false;
                            try {
                                let rdata = await this.$http(
                                    {
                                        project_add_domain: '添加项目域名',
                                    },
                                    {
                                        project_name: this.data.name,
                                        domains: domainList,
                                    }
                                );
                                this.domainInfo = '';
                                await this.get_domain_list();
                                site.render_domain_result_table(rdata)
                            } catch (e) {
                                this.$msg(e);
                            }
                        },
                        // 删除域名信息
                        del_domain_info(row) {
                            bt.confirm(
                                {
                                    title: '删除域名【' + row.name + '】',
                                    msg: '您真的要从站点中删除这个域名吗？',
                                },
                                async () => {
                                    try {
                                        let rdata = await this.$http(
                                            {
                                                project_remove_domain: '删除项目域名',
                                            },
                                            {
                                                project_name: this.data.name,
                                                domain: row.name,
                                            }
                                        );
                                        await this.get_domain_list();
                                        this.$msg(rdata);
                                    } catch (e) {
                                        this.$msg(e);
                                    }
                                }
                            );
                        },
                        // 设置禁用
                        set_disable(row) {
                            switch (this.$request) {
                                case 'java':
                                    if (this.project_type < 3 && row.name === this.data.name)
                                        return false;
                                    break;
                            }
                            return true;
                        },
                        // 批量删除
                        onBatchDel(checkList = []) {
                            bt.show_confirm(
                                '批量删除域名',
                                '<span style="color:red">同时删除选中的域名，是否继续？</span>',
                                async () => {
                                    try {
                                        const list = [];
                                        const domainList = this.domainList;
                                        checkList.forEach(i => list.push(domainList[i]));
                                        let item,
                                            res,
                                            html = '';
                                        let { name } = this.data;
                                        let text = `正在执行批量删除域名，<span class="batch_progress">进度:0/${list.length}</span>,请稍候...`;
                                        let loadT = layer.msg(text, {
                                            icon: 16,
                                            skin: 'batch_tips',
                                            shade: 0.3,
                                            time: 0,
                                            area: '400px',
                                        });
                                        for (let i = 0; i < list.length; i++) {
                                            item = list[i];
                                            $('.batch_tips.layui-layer .batch_progress').html(
                                                `进度:${i + 1}/${list.length}`
                                            );
                                            res = await this.$http(
                                                {
                                                    project_remove_domain: false,
                                                    verify: false,
                                                },
                                                {
                                                    project_name: name,
                                                    domain: item.name,
                                                }
                                            );
                                            html += `
                            <tr>
                              <td><span class="size_ellipsis" style="width: 120px;" title="${
                                                item.name
                                            }">${item.name}</span></td>
                              <td class="text-right"><span style="color: ${
                                                res.status ? '#20a53a' : 'red'
                                            }">${res.msg}</span></td>
                            </tr>
                          `;
                                        }
                                        layer.close(loadT);
                                        await this.get_domain_list();
                                        this.$refs['domainTable'].reset_checked();
                                        this.batch_success_table({
                                            html,
                                            th: '项目名称',
                                            title: '批量删除项目',
                                        });
                                    } catch (e) {
                                        this.$msg(e);
                                    }
                                }
                            );
                        },
                        batch_success_table(
                            { th, title, html } = { th: '', title: '', html: '' }
                        ) {
                            bt.open({
                                type: 1,
                                title: title,
                                area: '350px',
                                shadeClose: false,
                                closeBtn: 2,
                                content: `
                        <div class="batch_title">
                          <span>
                            <span class="batch_icon"></span>
                            <span class="batch_text">${title}操作完成！</span>
                          </span>
                        </div>
                        <div class="batch_tabel divtable" style="margin: 15px 30px 15px 30px; overflow: auto; max-height: 226px; border: 1px solid #ddd;">
                          <table class="table table-hover" id="batch_tabel" style="border: none;">
                            <thead>
                              <tr>
                                <th>${th}</th>
                                <th class="text-right">操作结果</th>
                              </tr>
                            </thead>
                            <tbody>${html}</tbody>
                          </table>
                        </div>`,
                                success() {
                                    bt.fixed_table('batch_tabel');
                                },
                            });
                        },
                    },
                    mounted() {
                        if (this.$request === 'java') {
                            let config = this.data.project_config;
                            switch (config.java_type) {
                                case 'springboot':
                                    this.project_type = 3;
                                    break;
                                case 'duli':
                                    this.project_type = 2;
                                    break;
                                case 'neizhi':
                                    this.project_type = 1;
                                    break;
                            }
                        }
                        this.get_domain_list();
                    },
                });
            
                // 网站管理 -通用模块-项目伪静态组件
                // Vue.component('bt-site-load-state',{
                //     template:`<div class="load_state_view">
                //             <bt-line label="PID" label="30px">\
                //                 <bt-select v-model="form.tomcat_version">
                //                     <bt-option v-for="(item,index) in tomcatList" :key="index" :title="item.title" :value="item.value"></bt-option>
                //                 </bt-select>
                //             </bt-line>
                //             <!--                  <bt-cust-table></bt-cust-table>-->
                //             <h3 class="tname">网络</h3>
                //             <bt-table :data="connectionsList">
                //                 <bt-table-column title="端口" width="100px" prop="port"></bt-table-column>
                //             </bt-table>
                //             <h3 class="tname">打开的文件列表</h3>
                //             <bt-table :data="openFilesList">
                //                 <bt-table-column title="端口" width="100px" prop="port"></bt-table-column>
                //             </bt-table>
                //         </div>`,
                //     props:{
                //         data:Object
                //     },
                //     data(){
                //         return {
                //             pidList:[],
                //             connectionsList:[],
                //             openFilesList:[],
                //             otherInfo:{}
                //         }
                //     },
                //     methods:{
                //         // 格式化项目信息
                //         format_project_load(){
                //             let data = this.data;
                //             for (const dataKey in data) {
                //                 this.pid.push(dataKey)
                //             }
                //             this.set_specify_pid_info(this.pidList[0])
                //         },
                //         // 设置指定PID信息
                //         set_specify_pid_info(pid){
                //             let info = this.data[pid]
                //             this.connectionsList = info.connections
                //             this.openFilesList = info.open_files
                //         }
                //     },
                //     mounted(){
                //         this.format_project_load()
                //     }
                // })
            
                Vue.component('bt-site-service-status', {
                    template: `<div class="soft-man-con pd10">
                        <p class="status">当前状态：<bt-link :title="data.run ? '运行中' : '未启动'"
                                                    :status="data.run"
                                                    :icon="data.run?'play':'pause'"></bt-link></p>
                        <div class="sfm-opt">
                            <bt-button :title="data.run?'停止':'启动'" @click="set_service_status((data.run ?'stop_project':'start_project'),data.name)"></bt-button>
                            <bt-button title="重启" @click="set_service_status('restart_project',data.name)"></bt-button>
                            </div>
                    </div>`,
                    props: {
                        data: {
                            type: [Object, Array],
                            default: function () {
                                return {
                                    run: false,
                                    name: '',
                                };
                            },
                        },
                    },
                    data() {
                        return {
                            run: this.data.run,
                        };
                    },
                    methods: {
                        async set_service_status(type, name) {
                            let param = {};
                            let info = {
                                stop_project: [
                                    '停止[' +
                                    name +
                                    ']项目，停用后将无法访问该项目，您真的要停用这个项目吗',
                                    '停止项目',
                                ],
                                start_project: [
                                    '即将启动[' + name + ']项目，是否继续操作？',
                                    '启动项目',
                                ],
                                restart_project: [
                                    '您确定要重启项目吗，当前项目可能会受到影响，继续操作?',
                                    '重启项目',
                                ],
                            };
                            param[type] = info[type][1] + '[' + name + ']';
                            try {
                                await this.$confirm({
                                    title: info[type][1] + '[' + name + ']',
                                    msg: info[type][0],
                                });
                                let rdata = await this.$http(param, {
                                    project_name: name,
                                });
                                if (type != 'restart_project' && !this.run && rdata.status) {
                                    this.run = !this.run;
                                    this.$parent.data.run = this.run;
                                }
            
                                // if (rdata.status && type == 'restart_project' && !this.run) {
                                // 	this.run = !this.run;
                                // } else if (rdata.status && type != 'restart_project') {
                                // }
                                // if (rdata.status) {
                                // }
                                this.$msg(rdata);
                            } catch (e) {
                                this.$msg(e);
                            }
                        },
                    },
                    mounted() {},
                });
            
                // 网站管理 - JAVA模块 - 项目表单
                Vue.component('bt-java-form', {
                    template: `<div :class="{'bt-form':true,'ptb15':!isAddForm}">
                            <bt-line label="项目类型">
                                <div class="btn-group " role="group">
                                    <button v-for="(item,index) in projectTypeList" :key="index" type="button"
                                            :class="{'btn':true,'btn-default':true,'btn-sm':true,'btn-success':item.value === form.project_type}"
                                            @click="cut_java_project_type(item,index)" :disabled="!isAddForm">
                                        <span>{{ item.title }}</span>
                                        <input type="checkbox" class="hide" v-model="form.project_type" :value="item.value"/>
                                    </button>
                                </div>
                                <bt-link class="mlr15" title="JAVA项目教程" href="https://www.bt.cn/bbs/thread-76217-1-1.html" target="_blank"></bt-link>
                            </bt-line>
                            <bt-line label="项目域名" v-if="form.project_type < 3">
                                <bt-text width="380px" v-model="form.domain" placeholder="请输入项目域名" :disabled="!isAddForm" @input="input_project_domain"/>
                            </bt-line>
                            <bt-line label="项目路径" v-if="form.project_type < 3">
                                <bt-text v-model="form.project_path" width="350px" class-name="mr10"
                                         id="project_path" placeholder="请输入或选择项目路径" icon="folder-open"
                                         @icon-event="select_path('project_path')" />
                            </bt-line>
                            <bt-line label="Tomcat版本" v-if="form.project_type < 3 && $root.updateView" >
                                <bt-select v-model="form.tomcat_version" :disabled="!isAddForm">
                                    <bt-option v-for="(item,index) in tomcatList" :key="index" :title="item.title" :value="item.value"></bt-option>
                                </bt-select>
                                <bt-link title="安装Tomcat其他版本" v-if="isAddForm" @click="$root.tomcat_manage_view"></bt-link>
                            </bt-line>
                            <bt-line label="项目jar路径" v-if="form.project_type > 2">
                                <bt-text width="350px" v-model="form.project_jar"
                                         class-name="mr10"
                                                                                                                                                                                                                                             id="project_jdr_path"
                                         :disabled="!isAddForm"
                                         placeholder="请输入或选择项目jar路径" :icon="isAddForm?'folder-open':false"
                                         @blur="blur_project_jar"
                                         @icon-event="select_path('project_jdr_path','file')"/>
                            </bt-line>
                            <bt-line label="项目名称" v-if="form.project_type > 2">
                                <bt-text width="380px" v-model="form.project_name"
                                         placeholder="选择项目文件，自动获取名称" :disabled="!isAddForm" @input="input_project_name"/>
                            </bt-line>
                            <bt-line label="项目端口" v-if="form.project_type > 1">
                                <bt-text width="180px" type="number" v-model="form.port"
                                         :placeholder="form.project_type < 3?'请输入项目端口':'选择项目文件，自动获取端口'" @input="input_project_port" @blur="blur_project_port" describe="* 请输入项目的真实端口，启动可重新设置"/>
                                <span></span>
                            </bt-line>
                            <div class="line " style="margin-left:100px;" v-if="!data.listen_ok && false">
                              <span class="bt_danger">项目端口可能有误，检测到当前项目监听了以下端口[ {{ data.listen.join('、') }} ]</span>
                            </div>
                            <bt-line label="项目JDK" v-if="form.project_type > 2">
                                <bt-select width="300px" v-model="form.project_jdk" @change="cut_project_jdk" v-if="$root.updateView">
                                    <bt-option v-for="(item,index) in jdkList" :key="index" :title="item.title" :value="item.value"></bt-option>
                                </bt-select>
                                <bt-link title="添加JDK信息" v-if="isAddForm" @click="$root.jdk_manage_view"></bt-link>
                            </bt-line>
                            <bt-line label="项目执行命令" v-if="form.project_type > 2">
                                <bt-text type="textarea" width="380px" line-height="20px" height="70px"
                                         :resize="true" :tips="true" v-model="form.project_cmd"
                                         placeholder="选择项目jar文件，自动获取项目执行命令"/>
                            </bt-line>
                            <bt-line label="远程调试开启" v-if="form.project_type > 2">
                                <bt-checkbox v-model="form.debug" label="设置远程调试，配合IDEA使用，生产环境慎用" @change="set_project_debug" :disabled="form.project_cmd === ''" :showTips="isAddForm" :tips="'请选择Java项目后，重新尝试'" />
                            </bt-line>
                            <bt-line label="项目用户" v-if="form.project_type > 2">
                                <bt-select width="150px" v-model="form.run_user" describe="* 无特殊需求请选择www用户">
                                    <bt-option v-for="(item,index) in projectUserList" :key="index" :title="item.title" :value="item.value"></bt-option>
                                </bt-select>
                            </bt-line>
                            <bt-line label="开机启动" v-if="form.project_type > 1">
                                <bt-checkbox v-model="form.auth" label="是否设置开机自动启动（默认自带守护进程每120秒检测一次）"/>
                            </bt-line>
                            <bt-line label="前后端分离" v-if="form.project_type == 3">
                                <bt-checkbox v-model="form.is_separation" label="是否设置前后端分离" :disabled="isSeparationDisabled || !isAddForm" :showTips="isAddForm" :tips="'请选择Java项目后，重新尝试'" @change="onSeparationChange" />
                            </bt-line>
                            <bt-line label="后端url" v-if="form.is_separation == 1">
                                <bt-text width="380px" v-model="form.api_url" :disabled="!isAddForm" placeholder="请输入后端url,例如：/api"/>
                            </bt-line>
                            <bt-line label="目标url" v-if="form.is_separation == 1">
                                <bt-text width="380px" v-model="form.host_url" :disabled="!isAddForm" placeholder="请输入目标url"/>
                            </bt-line>
                            <bt-line label="前端根目录" v-if="form.is_separation == 1">
                                <bt-text width="350px" class-name="mr10" id="static_path" v-model="form.static_path"
                                  :disabled="!isAddForm" :icon="isAddForm?'folder-open':false"
                                  placeholder="请输入或选择前端根目录"
                                  @icon-event="select_path('static_path')" />
                            </bt-line>
                            <bt-line label="项目备注">
                                <bt-text width="380px" v-model="form.project_ps"
                                         placeholder="请输入项目备注,非必填"/>
                            </bt-line>
                            <bt-line label="绑定域名" v-if="isAddForm && form.project_type === 3">
                                <bt-text type="textarea" width="380px" height="120px"
                                         v-model="form.domains"
                                         :placeholder="['如果需要绑定外网，请输入需要绑定的域名，该选项可为空','如需填写多个域名，请换行填写，每行一个域名，默认为80端口','泛解析添加方法 *.domain.com', '暂不支持添加端口格式的域名 *.domain.com:88']"/>
                            </bt-line>
                            <bt-line label="" v-if="!isAddForm">
                                <bt-button type="success" title="保存项目配置" @click="editing_project_info"></bt-button>
                            </bt-line>
                        </div>`,
                    props: {
                        data: {
                            type: Object,
                            default: function () {
                                return {
                                    listen_ok: true,
                                    listen: [],
                                };
                            },
                        },
                        config: {
                            type: Object,
                            default: function () {
                                return {
                                    jdkList: [],
                                    tomcatList: [],
                                    form: {},
                                };
                            },
                        },
                    },
                    computed: {
                        isSeparationDisabled() {
                            const { project_name: name, port, project_jdk: jdk } = this.form;
                            return name == '' || port == '' || jdk == '';
                        },
                    },
                    data() {
                        return {
                            projectTypeList: [
                                {
                                    title: 'Spring_boot',
                                    value: 3,
                                },
                                {
                                    title: '内置项目',
                                    value: 1,
                                },
                                {
                                    title: '独立项目',
                                    value: 2,
                                },
                            ],
                            projectUserList: [
                                {
                                    title: 'www',
                                    value: 'www',
                                },
                                {
                                    title: 'springboot',
                                    value: 'springboot',
                                },
                                {
                                    title: 'root',
                                    value: 'root',
                                },
                            ],
                            form: this.config.form,
                            jdkList: this.config.jdkList,
                            tomcatList: this.config.tomcatList,
                            isAddForm: true,
                            help_list: [],
                        };
                    },
                    methods: {
                        /**
                         * @description 切换java项目类型
                         * @param {object} item 选中的数据项
                         */
                        cut_java_project_type(item) {
                            this.form.project_type = item.value;
                        },
                        /**
                         * @description 输入项目域名，同步其他输入内容
                         */
                        input_project_domain() {
                            if (!this.isAddForm) return;
                            this.form.project_ps = this.form.domain;
                            this.form.project_path = '/www/wwwroot/' + this.form.domain;
                        },
                        /**
                         * @description 输入项目名称，同步其他输入内容
                         */
                        input_project_name() {
                            this.form.project_ps = this.form.project_name;
                            if (this.form.is_separation == 1) {
                                this.form.static_path = '/www/wwwroot/' + this.form.project_name;
                            }
                        },
                        /**
                         * @description 输入项目端口号，同步其他输入内容
                         */
                        input_project_port() {
                            this.form.host_url = 'http://127.0.0.1:' + this.form.port;
                        },
                        async set_project_debug() {
                            if (this.form.debug) {
                                try {
                                    await this.$confirm({
                                        title: '警告',
                                        msg: '此功能为远程调试配合IDEA使用，不建议在生产环境使用，调试端口随机生成，端口号请查看生成的命令,默认不开放此端口,需自行开放。',
                                    });
                                    await this.get_java_project_cmd(this.form, 3);
                                } catch (e) {
                                    this.form.debug = false;
                                }
                            } else {
                                await this.get_java_project_cmd(this.form, 3);
                            }
                        },
            
                        /**
                         * @description 选择文件路径
                         * @param name {string} 需要选择的名称
                         * @param type {string} 选择类型,默认为目录
                         */
                        select_path(name, type) {
                            this.$tryCatch(() => {
                                bt.select_path(name, type || 'dir', async path => {
                                    switch (name) {
                                        case 'static_path':
                                            this.form.static_path = path;
                                            break;
                                        case 'project_path':
                                            this.form.project_path = path;
                                            break;
                                        case 'project_jdr_path':
                                            let list = path.split('/'),
                                                fileName = list[list.length - 1];
                                            fileName = fileName.split('.')[0];
                                            this.form.project_name = fileName;
                                            this.form.project_ps = fileName;
                                            this.form.project_jar = path;
                                            await this.get_java_project_cmd(this.form);
                                            break;
                                    }
                                });
                            });
                        },
                        /**
                         * @description 失去焦点jdr目录事件
                         */
                        async blur_project_jar() {
                            if (this.form.project_jar === '/www/wwwroot' || !this.isAddForm)
                                return false;
                            await this.get_java_project_cmd(this.form);
                        },
                        /**
                         * @description 失去焦点项目端口
                         */
                        async blur_project_port() {
                            if (this.form.project_jar === '/www/wwwroot') return false;
                            if (!this.isAddForm && this.form.project_type != 3) return false;
                            await this.get_java_project_cmd(this.form, 1);
                        },
                        /**
                         * @description 切换项目JDK事件
                         */
                        async cut_project_jdk() {
                            if (this.form.project_jar === '/www/wwwroot') return false;
                            // if (!this.isAddForm) {
                            //   await this.reset_java_project_cmd(this.form)
                            // } else {
                            //   await this.get_java_project_cmd(this.form)
                            // }
                            await this.get_java_project_cmd(this.form, 2);
                        },
                        /**
                         * @description 获取java项目的执行命令
                         * @param {object} param 请求参数
                         * @return {Promise}
                         */
                        async get_java_project_cmd(param, type = 0) {
                            try {
                                let rdata = await this.$http(
                                    {
                                        return_cmd: '获取项目执行命令',
                                    },
                                    {
                                        type: type,
                                        project_name: param.project_name,
                                        project_cmd: param.project_cmd,
                                        project_jar: param.project_jar,
                                        project_jdk: param.project_jdk,
                                        debug: param.debug,
                                        port: param.port,
                                    }
                                );
                                this.form.project_cmd = rdata.msg;
                                this.form.port = rdata.msg.match(/([0-9]*)$/)[0];
                            } catch (e) {
                                this.$msg(e);
                            }
                        },
                        /**
                         * @description 重置项目执行命令
                         * @param param
                         */
                        async reset_java_project_cmd(param) {
                            try {
                                let rdata = await this.$http(
                                    {
                                        return_jdkcmd: '重置项目命令',
                                    },
                                    {
                                        jdK_path: param.project_jdk,
                                        cmd: param.project_cmd,
                                    }
                                );
                                this.form.project_cmd = rdata.msg;
                            } catch (e) {
                                this.$msg(e);
                            }
                        },
                        /**
                         * @description 编辑项目信息
                         */
                        async editing_project_info() {
                            try {
                                let rdata = await this.$http(
                                    {
                                        modify_project: '修改项目配置',
                                    },
                                    Object.assign(
                                        {
                                            project_name: this.data.name,
                                        },
                                        this.form
                                    )
                                );
                                this.$parent.data = await this.$root.get_project_info(this.data.name);
                                this.$msg(rdata);
                                this.$parent.config &&
                                this.$parent.config.getProjectList &&
                                this.$parent.config.getProjectList();
                            } catch (e) {
                                this.$msg(e);
                            }
                        },
                        onSeparationChange() {
                            const { is_separation, port, project_name: name } = this.form;
                            if (is_separation == 1) {
                                this.form.host_url = 'http://127.0.0.1:' + port;
                                this.form.static_path = '/www/wwwroot/' + name;
                            } else {
                                this.form.host_url = '';
                                this.form.static_path = '';
                            }
                        },
                    },
                    mounted() {
                        if (this.$parent.config && this.$parent.data) {
                            let row = this.$parent.data;
                            let project_config = row.project_config;
                            this.isAddForm = false;
                            let config = this.$parent.config;
                            this.jdkList = config.jdkList;
                            this.tomcatList = config.tomcatList;
                            this.form = Object.assign(config.form, {
                                project_type:
                                    project_config.java_type === 'springboot'
                                        ? 3
                                        : project_config.java_type === 'duli'
                                            ? 2
                                            : 1, // 项目列表
                                project_name: row.name, // 项目名称，仅项目为3
                                domain: row.name, // 仅项目类型为独立项目和内置项目，需要传递域名作为项目名称
                                domains: '', // 项目名称，仅项目为3
                                project_path:
                                    project_config.java_type !== 'springboot' ? row.path : '', // 项目路径，仅项目类型为独立项目和内置项目
                                project_jdk: project_config.project_jdk || '', // 项目JDK，仅项目为3
                                project_jar: project_config.project_jar || '', // 项目JDR路径，仅项目为3
                                project_cmd: project_config.project_cmd || '', // 项目执行命令，仅项目为3
                                run_user: project_config.run_user || 'www', // 项目执行用户，仅项目为3
                                tomcat_version: parseInt(project_config.tomcat_version || '0'), // tomcat版本,仅项目类型为独立项目和内置项目
                                project_ps: row.ps, // 描述字段
                                port: project_config.port, //项目端口
                                auth: parseInt(project_config.auth), //是否开启启动
                                is_separation: parseInt(project_config.is_separation), // 前后端分离
                                api_url: project_config.api_url, // 后端url
                                host_url: project_config.host_url, // 目标url
                                static_path: project_config.static_path, // 前端根目录
                                debug: row.debug ? 1 : 0,
                            });
                        }
                    },
                });
            
                // 网站管理-项目SSL组件
                // Vue.component('bt-porject-ssl',{})
            
                // 网站管理-项目
                //
            });
            