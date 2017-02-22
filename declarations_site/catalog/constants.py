OLD_DECLARATION_INDEX = 'declarations_v2'
NACP_DECLARATION_INDEX = 'nacp_declarations'
CATALOG_INDICES = (OLD_DECLARATION_INDEX, NACP_DECLARATION_INDEX)

CATALOG_INDEX_SETTINGS = {
    'index.mapping.total_fields.limit': 5000,
    'index.max_result_window': 1000000
}
