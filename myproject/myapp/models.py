# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuditAuditlog(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    action = models.CharField(max_length=200)
    action_details = models.TextField()
    obj_id = models.IntegerField(blank=True, null=True)
    module = models.CharField(max_length=50)
    related_object_id = models.IntegerField(blank=True, null=True)
    performed_by_id = models.BigIntegerField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'audit_auditlog'


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True)
    content = models.TextField()
    message_type = models.CharField(max_length=32)
    metadata = models.JSONField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_content_encrypted = models.BooleanField()
    user_id = models.BigIntegerField()
    conversation_id = models.UUIDField()

    class Meta:
        managed = False
        db_table = 'chat_message'


class ContractsContract(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    project_title = models.CharField(max_length=255, blank=True, null=True)
    counter_party = models.CharField(max_length=255, blank=True, null=True)
    project_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_open_ended = models.BooleanField()
    status = models.CharField(max_length=50, blank=True, null=True)
    site_address_line_1 = models.CharField(max_length=500, blank=True, null=True)
    site_address_line_2 = models.CharField(max_length=500, blank=True, null=True)
    site_city = models.CharField(max_length=100, blank=True, null=True)
    site_state = models.CharField(max_length=100, blank=True, null=True)
    site_zip_code = models.CharField(max_length=20, blank=True, null=True)
    site_country = models.CharField(max_length=2, blank=True, null=True)
    contract_parent_id = models.BigIntegerField(blank=True, null=True)
    contract_type_id = models.BigIntegerField(blank=True, null=True)
    created_by_id = models.BigIntegerField(blank=True, null=True)
    law_firm_id = models.BigIntegerField(blank=True, null=True)
    organisation_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'contracts_contract'


class ContractsContractdebt(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    financer_name = models.CharField(max_length=255, blank=True, null=True)
    debt_period = models.CharField(max_length=100, blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    loan_repayment_date = models.DateField(blank=True, null=True)
    contract_id = models.BigIntegerField()

    class Meta:
        db_table = 'contracts_contractdebt'


class ContractsContractdocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    document_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    contract_id = models.BigIntegerField()
    document_type_id = models.BigIntegerField(blank=True, null=True)
    uploaded_by_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'contracts_contractdocument'


class ContractsContractuserrole(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    contract_id = models.BigIntegerField()
    role_id = models.BigIntegerField()
    user_id = models.BigIntegerField()

    class Meta:
        db_table = 'contracts_contractuserrole'


class ContractsNegativecovenant(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    contract_id = models.BigIntegerField()

    class Meta:
        db_table = 'contracts_negativecovenant'


class ContractsNegativecovenantdocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    document_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    negative_covenant_id = models.BigIntegerField()
    uploaded_by_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'contracts_negativecovenantdocument'


class ContractsPaymentreceived(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    total_received = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    deductions = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    hold_backs = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    delay_in_payment_days = models.IntegerField(blank=True, null=True)
    financial_milestone_id = models.BigIntegerField()

    class Meta:
        db_table = 'contracts_paymentreceived'


class ContractsSuspensionevent(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50)
    contract_id = models.BigIntegerField()

    class Meta:
        db_table = 'contracts_suspensionevent'


class ContractsSuspensioneventdocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    document_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    suspension_event_id = models.BigIntegerField()
    uploaded_by_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'contracts_suspensioneventdocument'


class ContractsSuspensioneventupdate(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    update_date = models.DateField()
    comment_text = models.TextField(blank=True, null=True)
    is_issue = models.BooleanField()
    is_resolved = models.BooleanField()
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_comment = models.TextField(blank=True, null=True)
    resolved_by_id = models.BigIntegerField(blank=True, null=True)
    suspension_event_id = models.BigIntegerField()
    user_id = models.BigIntegerField()

    class Meta:
        db_table = 'contracts_suspensioneventupdate'


class ContractsSuspensioneventupdatedocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    document_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_resolution_document = models.BooleanField()
    suspension_event_update_id = models.BigIntegerField()
    uploaded_by_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'contracts_suspensioneventupdatedocument'


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_title_encrypted = models.BooleanField()
    task_id = models.BigIntegerField(blank=True, null=True)
    user_id = models.BigIntegerField()

    class Meta:
        db_table = 'conversation'


class DefenderAccessattempt(models.Model):
    id = models.AutoField(primary_key=True)
    user_agent = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    http_accept = models.CharField(max_length=1025)
    path_info = models.CharField(max_length=255)
    attempt_time = models.DateTimeField()
    login_valid = models.BooleanField()

    class Meta:
        db_table = 'defender_accessattempt'


class EntitiesLawfirm(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'entities_lawfirm'


class EntitiesOrganisation(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField()

    class Meta:
        db_table = 'entities_organisation'


class ExtensionsScheduleextensiondocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    document_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    document_type = models.CharField(max_length=50)
    uploaded_by_id = models.BigIntegerField(blank=True, null=True)
    schedule_extension_id = models.BigIntegerField()

    class Meta:
        db_table = 'extensions_scheduleextensiondocument'


class ExtensionsScheduleextensionhistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    extension_type = models.CharField(max_length=100)
    initial_start_date = models.DateField(blank=True, null=True)
    initial_end_date = models.DateField(blank=True, null=True)
    revised_start_date = models.DateField(blank=True, null=True)
    revised_end_date = models.DateField(blank=True, null=True)
    reason = models.TextField()
    force_measure_noticed = models.BooleanField()
    force_measure_notice_date = models.DateField(blank=True, null=True)
    force_measure_approved_by = models.CharField(max_length=500)
    suspension_of_work = models.BooleanField()
    suspension_notice = models.TextField()
    suspension_approved_by = models.CharField(max_length=500)
    account_type = models.CharField(max_length=100)
    response = models.BooleanField()
    change_of_scope = models.BooleanField()
    change_of_scope_issued = models.BooleanField()
    change_of_scope_done = models.BooleanField()
    change_of_scope_approved_by = models.CharField(max_length=500)
    approximate_cost_impact = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    reason_for_proceeding = models.TextField()
    informed_to_employer = models.BooleanField()
    contract_id = models.BigIntegerField()

    class Meta:
        db_table = 'extensions_scheduleextensionhistory'


class FinancialMilestones(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    milestone_title = models.CharField(max_length=255)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    cost_overrun = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    contract_id = models.BigIntegerField()

    class Meta:
        db_table = 'financial_milestones'


class MastersContractpermission(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'masters_contractpermission'


class MastersContractroletype(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    role_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    display_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'masters_contractroletype'


class MastersContractroletypePermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    contractroletype_id = models.BigIntegerField()
    contractpermission_id = models.BigIntegerField()

    class Meta:
        db_table = 'masters_contractroletype_permissions'


class MastersContracttype(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'masters_contracttype'


class MastersDocumenttype(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100)

    class Meta:
        db_table = 'masters_documenttype'


class MastersGroupprofile(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    group_id = models.IntegerField()
    display_name = models.CharField(max_length=100)
    group_entity_type = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'masters_groupprofile'


class MastersTasktype(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'masters_tasktype'


class ObligationsEscalationmatrix(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    level = models.IntegerField()
    days = models.IntegerField()
    is_triggered = models.BooleanField()
    triggered_at = models.DateTimeField(blank=True, null=True)
    notify_role_id = models.BigIntegerField()
    obligation_id = models.BigIntegerField()

    class Meta:
        db_table = 'obligations_escalationmatrix'


class ObligationsObligation(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    obligation_title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    page_section_reference = models.CharField(max_length=100, blank=True, null=True)
    extend_timeline_approval = models.CharField(max_length=50, blank=True, null=True)
    obligation_type = models.CharField(max_length=50)
    party_type = models.CharField(max_length=50)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    consequence = models.TextField(blank=True, null=True)
    exception = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    progress_percentage = models.IntegerField()
    assigned_role_id = models.BigIntegerField()
    contract_id = models.BigIntegerField()
    copied_reference_id = models.BigIntegerField(blank=True, null=True)
    obligation_document_id = models.BigIntegerField(blank=True, null=True)
    obligation_parent_id = models.BigIntegerField(blank=True, null=True)
    closing_details = models.TextField(blank=True, null=True)
    risk_category = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'obligations_obligation'


class ObligationsObligationtimelineextension(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    request_date = models.DateTimeField()
    new_start_date = models.DateField(blank=True, null=True)
    new_end_date = models.DateField(blank=True, null=True)
    reason_for_delay = models.TextField()
    delay_anticipated_in_project = models.BooleanField(blank=True, null=True)
    impact_on_project = models.TextField(blank=True, null=True)
    impact_under_contract = models.TextField(blank=True, null=True)
    remedial_actions_possible = models.BooleanField(blank=True, null=True)
    remedial_action_description = models.TextField(blank=True, null=True)
    approval_status = models.CharField(max_length=50)
    approval_date = models.DateTimeField(blank=True, null=True)
    approval_remarks = models.TextField(blank=True, null=True)
    approved_by_id = models.BigIntegerField(blank=True, null=True)
    obligation_id = models.BigIntegerField()
    requested_by_id = models.BigIntegerField()

    class Meta:
        db_table = 'obligations_obligationtimelineextension'


class ObligationsTimelineextensiondocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    document_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    document_type = models.CharField(max_length=50, blank=True, null=True)
    timeline_extension_id = models.BigIntegerField()
    uploaded_by_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'obligations_timelineextensiondocument'


class ObligationsTimelineextensionimpactedtask(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    impact_description = models.TextField(blank=True, null=True)
    impacted_task_id = models.BigIntegerField()
    timeline_extension_id = models.BigIntegerField()

    class Meta:
        db_table = 'obligations_timelineextensionimpactedtask'


class PaymentActivities(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    budget = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    percentage_work_done = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    percentage_spent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    cost_overrun = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    action_taken = models.TextField(blank=True, null=True)
    financial_milestone_id = models.BigIntegerField()

    class Meta:
        db_table = 'payment_activities'


class PaymentSchedules(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    vendor_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    due_date = models.DateField(blank=True, null=True)
    payment_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20)
    financial_milestone_id = models.BigIntegerField()

    class Meta:
        db_table = 'payment_schedules'


class TasksContracttask(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    task_title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    work_type = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    task_status = models.CharField(max_length=50, blank=True, null=True)
    progress_percentage = models.IntegerField()
    assigned_to_role_id = models.BigIntegerField(blank=True, null=True)
    obligation_id = models.BigIntegerField()
    parent_task_id = models.BigIntegerField(blank=True, null=True)
    task_type_id = models.BigIntegerField(blank=True, null=True)
    closing_details = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'tasks_contracttask'


class TasksTaskcommunication(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_flagged = models.BooleanField()
    task_id = models.BigIntegerField()
    user_id = models.BigIntegerField()

    class Meta:
        db_table = 'tasks_taskcommunication'


class TasksTaskcommunicationdocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    document_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    communication_id = models.BigIntegerField()
    document_type_id = models.BigIntegerField(blank=True, null=True)
    uploaded_by_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'tasks_taskcommunicationdocument'


class TasksTaskdocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    document_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    document_type_id = models.BigIntegerField(blank=True, null=True)
    task_id = models.BigIntegerField()
    uploaded_by_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'tasks_taskdocument'


class TasksTaskfieldchange(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    field_name = models.CharField(max_length=255)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    task_update_id = models.BigIntegerField()

    class Meta:
        db_table = 'tasks_taskfieldchange'


class TasksTaskupdate(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    update_date = models.DateField()
    comment_text = models.TextField(blank=True, null=True)
    is_issue = models.BooleanField()
    is_resolved = models.BooleanField()
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_comment = models.TextField(blank=True, null=True)
    resolved_by_id = models.BigIntegerField(blank=True, null=True)
    task_id = models.BigIntegerField()
    user_id = models.BigIntegerField()

    class Meta:
        db_table = 'tasks_taskupdate'


class TasksTaskupdatedocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    document_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_resolution_document = models.BooleanField()
    document_type_id = models.BigIntegerField(blank=True, null=True)
    update_id = models.BigIntegerField()
    uploaded_by_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'tasks_taskupdatedocument'


class UsersOrganisationaccess(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    law_firm_id = models.BigIntegerField()
    organisation_id = models.BigIntegerField()
    user_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'users_organisationaccess'


class UsersUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=10, blank=True, null=True)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()

    class Meta:
        db_table = 'users_user'


class UsersUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    group_id = models.IntegerField()

    class Meta:
        db_table = 'users_user_groups'


class UsersUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    permission_id = models.IntegerField()

    class Meta:
        db_table = 'users_user_user_permissions'


class UsersUserlawfirmaccess(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    group_id = models.IntegerField()
    law_firm_id = models.BigIntegerField()
    user_id = models.BigIntegerField()

    class Meta:
        db_table = 'users_userlawfirmaccess'

