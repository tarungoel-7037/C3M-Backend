# ── Success message codes (2xxx / 1xxx) ──────────────────────────────────────

class SuccessCode:
    DEFAULT             = 2000
    USER_CREATED        = 2001
    LOGIN               = 2002
    LOGOUT              = 2003
    PROFILE_RETRIEVED   = 1406
    PASSWORD_CHANGED    = 1010


class SuccessMessage:
    DEFAULT             = 'Operation completed successfully.'
    USER_CREATED        = 'User created successfully.'
    LOGIN               = 'Login successful.'
    LOGOUT              = 'Logout successful.'
    PROFILE_RETRIEVED   = 'Current user information retrieved successfully.'
    PASSWORD_CHANGED    = 'Password changed successfully.'


# ── Error message codes (3xxx) ────────────────────────────────────────────────

class ErrorCode:
    DEFAULT             = 3000
    INVALID_JSON        = 3001
    INVALID_CREDENTIALS = 3002
    AUTH_REQUIRED       = 3003
    MISSING_FIELDS      = 3004
    PASSWORD_MISMATCH   = 3005
    USERNAME_EXISTS     = 3006
    EMAIL_EXISTS        = 3007
    PASSWORD_INVALID    = 3008
    WRONG_OLD_PASSWORD  = 3009


class ErrorMessage:
    DEFAULT             = 'An unexpected error occurred.'
    INVALID_JSON        = 'Invalid JSON body.'
    INVALID_CREDENTIALS = 'Invalid credentials provided.'
    AUTH_REQUIRED       = 'Authentication required.'
    MISSING_FIELDS      = '{fields} are required.'
    PASSWORD_MISMATCH   = 'Passwords do not match.'
    USERNAME_EXISTS     = 'Username already exists.'
    EMAIL_EXISTS        = 'Email already exists.'
    PASSWORD_INVALID    = 'Password validation failed.'
    WRONG_OLD_PASSWORD  = 'Old password is incorrect.'
