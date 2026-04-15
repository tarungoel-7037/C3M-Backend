# ── Success message codes (2xxx / 1xxx) ──────────────────────────────────────

class SuccessCode:
    DEFAULT             = 2000
    USER_CREATED        = 2001
    LOGIN               = 2002
    LOGOUT              = 2003
    PROFILE_RETRIEVED   = 1406
    PASSWORD_CHANGED    = 1010
    USER_ADDED_TO_ORG   = 2004
    USER_UPDATED        = 2005
    USER_REMOVED        = 2006
    USERS_LISTED        = 1400
    USER_RETRIEVED      = 2008
    CONTRACT_CREATED    = 2009
    OBLIGATION_CREATED  = 1241
    OBLIGATIONS_LISTED  = 2010
    OBLIGATION_RETRIEVED = 2011
    OBLIGATION_UPDATED  = 2012
    OBLIGATION_DELETED  = 2013
    CONTRACT_RETRIEVED = 2014
    CONTRACT_DELETED   = 2015
    TASKS_LISTED        = 1270
    TASK_CREATED        = 1271
    TASK_RETRIEVED      = 1272
    TASK_UPDATED        = 1273
    TASK_DELETED        = 1274
    CONTRACT_TYPES_RETRIEVED = 1600
    CONTRACT_ROLE_TYPES_RETRIEVED = 1601
    CONTRACT_ROLE_CREATED = 1602
    TASK_TYPES_RETRIEVED = 1603
    GROUPS_RETRIEVED = 1604
    CONTRACT_RESPONSIBILITY_CREATED = 1605


class SuccessMessage:
    DEFAULT             = 'Operation completed successfully.'
    USER_CREATED        = 'User created successfully.'
    LOGIN               = 'Login successful.'
    LOGOUT              = 'Logout successful.'
    PROFILE_RETRIEVED   = 'Current user information retrieved successfully.'
    PASSWORD_CHANGED    = 'Password changed successfully.'
    USER_ADDED_TO_ORG   = 'User added to organisation successfully.'
    USER_UPDATED        = 'User updated successfully.'
    USER_REMOVED        = 'User removed from organisation successfully.'
    USERS_LISTED        = 'Users retrieved successfully'
    USER_RETRIEVED      = 'User retrieved successfully.'
    CONTRACT_CREATED    = 'Contract created successfully.'
    OBLIGATION_CREATED  = 'Obligation created successfully'
    OBLIGATIONS_LISTED  = 'Obligations retrieved successfully.'
    OBLIGATION_RETRIEVED = 'Obligation retrieved successfully.'
    OBLIGATION_UPDATED  = 'Obligation updated successfully.'
    OBLIGATION_DELETED  = 'Obligation deleted successfully.'
    TASKS_LISTED        = 'Tasks retrieved successfully.'
    TASK_CREATED        = 'Task created successfully.'
    TASK_RETRIEVED      = 'Task retrieved successfully.'
    TASK_UPDATED        = 'Task updated successfully.'
    TASK_DELETED        = 'Task deleted successfully.'
    CONTRACT_RETRIEVED = 'Contract retrieved successfully.'
    CONTRACT_DELETED   = 'Contract deleted successfully.'
    CONTRACT_TYPES_RETRIEVED = 'Contract types retrieved successfully.'
    CONTRACT_ROLE_TYPES_RETRIEVED = 'Contract role types retrieved successfully.'
    CONTRACT_ROLE_CREATED = 'Contract role created successfully.'
    TASK_TYPES_RETRIEVED = 'Task types retrieved successfully.'
    GROUPS_RETRIEVED = 'Groups retrieved successfully.'
    CONTRACT_RESPONSIBILITY_CREATED = 'Contract responsibility assigned successfully.'


class AuditModule:
    CONTRACTS = 'contracts'
    CONTRACT_DOCUMENTS = 'contract_document'
    OBLIGATIONS = 'obligations'
    TASKS = 'tasks'
    USERS = 'users'
    MASTERS = 'masters'
    CONTRACT_RESPONSIBILITY = 'contract_responsibility'


class AuditAction:
    CREATE_CONTRACT = 'Create Contract'
    DELETE_CONTRACT = 'Delete Contract'
    CREATE_OBLIGATION = 'Create Obligation'
    UPDATE_OBLIGATION = 'Update Obligation'
    DELETE_OBLIGATION = 'Delete Obligation'
    UPLOAD_CONTRACT_DOCUMENT = 'Upload Contract Document'
    DELETE_CONTRACT_DOCUMENT = 'Delete Contract Document'
    CREATE_CONTRACT_TASK = 'Create Contract Task'
    UPDATE_CONTRACT_TASK = 'Update Contract Task'
    DELETE_CONTRACT_TASK = 'Delete Contract Task'
    CREATE_CONTRACT_ROLE = 'Create Contract Role'
    ASSIGN_CONTRACT_RESPONSIBILITY = 'Assign Contract Responsibility'
    CREATE_USER = 'Create User'
    UPDATE_USER = 'Update User'
    REMOVE_USER = 'Remove User'
    ADD_ORGANISATION_USER = 'Add Organisation User'
    UPDATE_ORGANISATION_USER = 'Update Organisation User'
    REMOVE_ORGANISATION_USER = 'Remove Organisation User'
    CHANGE_PASSWORD = 'Change Password'
    DELETE_CONTRACT_DOCUMENT = 'Delete Contract Document'
    CREATE_CONTRACT_TASK = 'Create Contract Task'
    UPDATE_CONTRACT_TASK = 'Update Contract Task'
    DELETE_CONTRACT_TASK = 'Delete Contract Task'


# ── Error message codes (3xxx) ────────────────────────────────────────────────

class ErrorCode:
    DEFAULT                 = 3000
    INVALID_JSON            = 3001
    INVALID_CREDENTIALS     = 3002
    AUTH_REQUIRED           = 3003
    MISSING_FIELDS          = 3004
    PASSWORD_MISMATCH       = 3005
    USERNAME_EXISTS         = 3006
    EMAIL_EXISTS            = 3007
    PASSWORD_INVALID        = 3008
    WRONG_OLD_PASSWORD      = 3009
    VALIDATION_ERROR        = 3010
    ORGANISATION_NOT_FOUND  = 3011
    GROUP_NOT_FOUND         = 3012
    USER_ALREADY_IN_ORG     = 3013
    USER_NOT_FOUND          = 3014
    CONTRACT_ROLE_NOT_FOUND = 3015
    PERMISSION_NOT_FOUND    = 3016
    USER_NOT_IN_ORG         = 3017
    RESPONSIBILITY_ALREADY_EXISTS = 3018


class ErrorMessage:
    DEFAULT                 = 'An unexpected error occurred.'
    INVALID_JSON            = 'Invalid JSON body.'
    INVALID_CREDENTIALS     = 'Invalid credentials provided.'
    AUTH_REQUIRED           = 'Authentication required.'
    MISSING_FIELDS          = '{fields} are required.'
    PASSWORD_MISMATCH       = 'Passwords do not match.'
    USERNAME_EXISTS         = 'Username already exists.'
    EMAIL_EXISTS            = 'Email already exists.'
    PASSWORD_INVALID        = 'Password validation failed.'
    WRONG_OLD_PASSWORD      = 'Old password is incorrect.'
    VALIDATION_ERROR        = 'Validation failed.'
    ORGANISATION_NOT_FOUND  = 'Organisation not found.'
    GROUP_NOT_FOUND         = 'Group not found.'
    USER_ALREADY_IN_ORG     = 'User is already a member of this organisation.'
    USER_NOT_FOUND          = 'User not found.'
    OBLIGATION_NOT_FOUND     = 'Obligation not found.'
    CONTRACT_NOT_FOUND       = 'Contract not found.'
    OBLIGATION_ACCESS_DENIED      = 'You do not have permission to access this obligation.'
    CONTRACT_ACCESS_DENIED        = 'You do not have permission to access this contract.'
    TASK_NOT_FOUND                = 'Task not found.'
    TASK_ACCESS_DENIED            = 'You do not have permission to access this task.'
    CONTRACT_TYPE_NOT_FOUND       = 'No contract types found'
    CONTRACT_ROLE_NOT_FOUND       = 'Contract role type not found.'
    PERMISSION_NOT_FOUND          = 'One or more permissions not found: {names}.'
    USER_NOT_IN_ORG               = 'User does not have access to this organisation.'
    RESPONSIBILITY_ALREADY_EXISTS = 'This user already has this role assigned on this contract.'
    RBAC_PERMISSION_DENIED        = 'You do not have permission to perform this action.'

