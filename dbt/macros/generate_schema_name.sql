{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is not none -%}
        {{ custom_schema_name | trim }}
    {%- elif node.fqn[1] == 'staging' -%}
        silver
    {%- elif node.fqn[1] == 'intermediate' -%}
        silver
    {%- elif node.fqn[1] == 'marts' -%}
        gold
    {%- else -%}
        {{ target.schema }}
    {%- endif -%}
{%- endmacro %}
