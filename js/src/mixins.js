export default {
    data: function(){
        return {
            errors: {},
        }
    },
    computed: {
        validation_error(){
            return Object.keys(this.errors).length > 0;
        }
    },
    methods: {
        /**
         *  Possible rules required, numeric, between:min,max, gt:number (greater than), gte:number (greater than or equal),
         *  lt:number (less than), lte:number (less than or equal to)
         **/
        validate(data, rules) {

            // tokenize the string
            let rules_ = {};
            Object.entries(rules).map(function (e) {
                const [key, ruleString] = e;
                let ruleString_ = ruleString.split("|");

                let ruleObject = {}
                ruleString_.forEach(function (rule) {
                    if (rule.includes(":")) {
                        let splitRule = rule.split(":");
                        ruleObject[splitRule[0]] = splitRule[1].split(",");
                    } else ruleObject[rule] = true;
                })
                return rules_[key] = ruleObject
            });

            // init error object and a method to add an error
            let errors = {};
            let add_error = function (key, message) {
                if (key in errors) errors[key].push(message);
                else errors[key] = [message];
                return errors;
            }

            // apply the rules
            Object.entries(data).forEach(function (e) {
                const [key, value] = e;

                if ('required' in rules_[key] && (value === null || value === "" || value === undefined)) add_error(key, "required");
                if ('numeric' in rules_[key] && Number.isNaN(value)) add_error(key, "numeric");
                if ('between' in rules_[key] && (value < rules_[key]['between'][0] || value > rules_[key]['between'][1])) add_error(key, "between");
                if ('gt' in rules_[key] && value <= rules_[key]['gt'][0]) add_error(key, "gt");
                if ('gte' in rules_[key] && value < rules_[key]['gte'][0]) add_error(key, "gte");
                if ('lt' in rules_[key] && value >= rules_[key]['lt'][0]) add_error(key, "lt");
                if ('lte' in rules_[key] && value > rules_[key]['lte'][0]) add_error(key, "lte");
            }.bind(this))

            this.errors = errors;

            return errors;
        },

        has_error(key){
            if(key in this.errors) return this.errors[key];
            return false;
        },

    }
}