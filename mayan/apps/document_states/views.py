from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _, ungettext

from acls.models import AccessEntry
from common.utils import encapsulate, generate_choices_w_labels
from common.views import (SingleObjectCreateView, SingleObjectDeleteView,
                          SingleObjectEditView, SingleObjectListView,
                          assign_remove)
from common.widgets import two_state_template
from documents.models import Document
from permissions.models import Permission

from .forms import WorkflowStateForm, WorkflowTransitionForm
from .models import Workflow
from .permissions import (PERMISSION_WORKFLOW_CREATE, PERMISSION_WORKFLOW_DELETE,
                          PERMISSION_WORKFLOW_EDIT, PERMISSION_WORKFLOW_VIEW,
                          PERMISSION_DOCUMENT_WORKFLOW_VIEW)


class DocumentWorkflowListView(SingleObjectListView):
    def dispatch(self, request, *args, **kwargs):
        try:
            Permission.objects.check_permissions(request.user, [PERMISSION_DOCUMENT_WORKFLOW_VIEW])
        except PermissionDenied:
            AccessEntry.objects.check_access(PERMISSION_DOCUMENT_WORKFLOW_VIEW, request.user, self.get_workflow())

        return super(DocumentWorkflowListView, self).dispatch(request, *args, **kwargs)

    def get_document(self):
        return get_object_or_404(Document, pk=self.kwargs['pk'])

    def get_queryset(self):
        return self.get_document().workflows.all()

    def get_context_data(self, **kwargs):
        context = super(DocumentWorkflowListView, self).get_context_data(**kwargs)
        context.update(
            {
                'hide_link': True,
                'object': self.get_document(),
                'title': _('Workflows of document: %s') % self.get_document()
            }
        )

        return context


class SetupWorkflowListView(SingleObjectListView):
    extra_context = {
        'title': _('Workflows'),
        'hide_link': True,
    }
    model = Workflow
    view_permission = PERMISSION_WORKFLOW_VIEW


class SetupWorkflowCreateView(SingleObjectCreateView):
    model = Workflow
    view_permission = PERMISSION_WORKFLOW_CREATE
    success_url = reverse_lazy('document_states:setup_workflow_list')


class SetupWorkflowEditView(SingleObjectEditView):
    model = Workflow
    object_permission = PERMISSION_WORKFLOW_EDIT
    success_url = reverse_lazy('document_states:setup_workflow_list')


class SetupWorkflowDeleteView(SingleObjectDeleteView):
    model = Workflow
    object_permission = PERMISSION_WORKFLOW_DELETE
    success_url = reverse_lazy('document_states:setup_workflow_list')


# States

class SetupWorkflowStateListView(SingleObjectListView):
    def dispatch(self, request, *args, **kwargs):
        try:
            Permission.objects.check_permissions(request.user, [PERMISSION_WORKFLOW_EDIT])
        except PermissionDenied:
            AccessEntry.objects.check_access(PERMISSION_WORKFLOW_EDIT, request.user, self.get_workflow())

        return super(SetupWorkflowStateListView, self).dispatch(request, *args, **kwargs)

    def get_workflow(self):
        return get_object_or_404(Workflow, pk=self.kwargs['pk'])

    def get_queryset(self):
        return self.get_workflow().states.all()

    def get_context_data(self, **kwargs):
        context = super(SetupWorkflowStateListView, self).get_context_data(**kwargs)
        context.update(
            {
                'hide_link': True,
                'object': self.get_workflow(),
                'title': _('States of workflow: %s') % self.get_workflow()
            }
        )

        return context


class SetupWorkflowStateCreateView(SingleObjectCreateView):
    form_class = WorkflowStateForm

    def dispatch(self, request, *args, **kwargs):
        try:
            Permission.objects.check_permissions(request.user, [PERMISSION_WORKFLOW_EDIT])
        except PermissionDenied:
            AccessEntry.objects.check_access(PERMISSION_WORKFLOW_EDIT, request.user, self.get_workflow())

        return super(SetupWorkflowStateCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SetupWorkflowStateCreateView, self).get_context_data(**kwargs)
        context.update(
            {
                'object': self.get_workflow(),
                'title': _('Create states for workflow: %s') % self.get_workflow()
            }
        )
        return context

    def get_workflow(self):
        return get_object_or_404(Workflow, pk=self.kwargs['pk'])

    def get_queryset(self):
        return self.get_workflow().states.all()

    def get_success_url(self):
        return reverse('document_states:setup_workflow_states', args=[self.kwargs['pk']])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.workflow = self.get_workflow()
        self.object.save()
        return super(SetupWorkflowStateCreateView, self).form_valid(form)


# Transitions

class SetupWorkflowTransitionListView(SingleObjectListView):
    def dispatch(self, request, *args, **kwargs):
        try:
            Permission.objects.check_permissions(request.user, [PERMISSION_WORKFLOW_EDIT])
        except PermissionDenied:
            AccessEntry.objects.check_access(PERMISSION_WORKFLOW_EDIT, request.user, self.get_workflow())

        return super(SetupWorkflowTransitionListView, self).dispatch(request, *args, **kwargs)

    def get_workflow(self):
        return get_object_or_404(Workflow, pk=self.kwargs['pk'])

    def get_queryset(self):
        return self.get_workflow().transitions.all()

    def get_context_data(self, **kwargs):
        context = super(SetupWorkflowTransitionListView, self).get_context_data(**kwargs)
        context.update(
            {
                'hide_link': True,
                'object': self.get_workflow(),
                'title': _('Transitions of workflow: %s') % self.get_workflow()
            }
        )

        return context


class SetupWorkflowTransitionCreateView(SingleObjectCreateView):
    form_class = WorkflowTransitionForm

    def dispatch(self, request, *args, **kwargs):
        try:
            Permission.objects.check_permissions(request.user, [PERMISSION_WORKFLOW_EDIT])
        except PermissionDenied:
            AccessEntry.objects.check_access(PERMISSION_WORKFLOW_EDIT, request.user, self.get_workflow())

        return super(SetupWorkflowTransitionCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SetupWorkflowTransitionCreateView, self).get_context_data(**kwargs)
        context.update(
            {
                'object': self.get_workflow(),
                'title': _('Create transitions for workflow: %s') % self.get_workflow()
            }
        )
        return context

    def get_workflow(self):
        return get_object_or_404(Workflow, pk=self.kwargs['pk'])

    def get_queryset(self):
        return self.get_workflow().transitions.all()

    def get_success_url(self):
        return reverse('document_states:setup_workflow_transitions', args=[self.kwargs['pk']])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.workflow = self.get_workflow()
        try:
            self.object.save()
        except IntegrityError:
            messages.error(self.request, _('Unable to save transition; integrity error.'))
            return super(SetupWorkflowTransitionCreateView, self).form_invalid(form)
        else:
            return HttpResponseRedirect(self.get_success_url())


def setup_workflow_document_types(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk)

    try:
        Permission.objects.check_permissions(request.user, [PERMISSION_WORKFLOW_EDIT])
    except PermissionDenied:
        AccessEntry.objects.check_access(PERMISSION_WORKFLOW_EDIT, request.user, workflow)

    return assign_remove(
        request,
        left_list=lambda: generate_choices_w_labels(workflow.get_document_types_not_in_workflow(), display_object_type=False),
        right_list=lambda: generate_choices_w_labels(workflow.document_types.all(), display_object_type=False),
        add_method=lambda x: workflow.document_types.add(x),
        remove_method=lambda x: workflow.document_types.remove(x),
        decode_content_type=True,
        extra_context={
            'main_title': _(u'Document types assigned the workflow: %s') % workflow,
            'object': workflow,
        }
    )
