MEMBERS_TABLE_QUERY = (
    "query MembersTable($canManageDepartments: Boolean!, "
    "$canReadEmployeeJobs: Boolean!, "
    "$employmentSetupStatuses: [MemberEmploymentSetupStatusEnum!], "
    "$employmentStatus: MemberEmploymentStatusEnum) {"
    " company {"
    " id"
    " members("
    " employmentSetupStatuses: $employmentSetupStatuses"
    " employmentStatus: $employmentStatus"
    " ) {"
    " nodes {"
    " id"
    " preferredFullName"
    " lastName"
    " jobTitle @include(if: $canReadEmployeeJobs)"
    " department @include(if: $canManageDepartments) {"
    " title"
    " }"
    " }"
    " }"
    " }"
    "}"
)

DEFAULT_MEMBERS_TABLE_VARIABLES = {
    "canManageDepartments": True,
    "canReadEmployeeJobs": True,
    "employmentSetupStatuses": ["COMPLETED"],
    "employmentStatus": "CURRENT_OR_PENDING_HIRE",
}


def build_members_table_payload(variables=None):
    return {
        "operationName": "MembersTable",
        "variables": variables if variables is not None else DEFAULT_MEMBERS_TABLE_VARIABLES,
        "query": MEMBERS_TABLE_QUERY,
    }
