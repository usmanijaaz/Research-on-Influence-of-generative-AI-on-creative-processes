from django.contrib import admin

from .models import (
    Participant,
    ExperimentCondition,
    ChatSession,
    ChatMessage,
    ExperimentPhase,
    Survey
)

@admin.register(ExperimentPhase)
class ExperimentalPhaseAdmin(admin.ModelAdmin):
    list_display=(
        "participant",
        "phase_number",
        "condition",
        "survey_completed",
        "started_at",
        "finished_at"
    )

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display=(
        "phase",
        "completed",
        "completed_at",
    )

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):

    list_display = (
        "participant_id",
        "role_order",
        "started_at",
        "finished_at",
        "session_duration"
    )

    def session_duration(self, obj):
        if obj.session_duration_minutes is None:
            return "-"

        return f"{obj.session_duration_minutes} min"

    session_duration.short_description = "Session Duration"

@admin.register(ExperimentCondition)
class ExperimentConditionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session_id",
        "phase",
        "total_messages",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "session_id",
    )

    ordering = (
        "-created_at",
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "role",
        "short_user_message",
        "created_at",
        "ai_response",
    )

    list_filter = (
        "role",
        "created_at",
    )

    search_fields = (
        "user_message",
        "ai_response",
    )

    ordering = (
        "-created_at",
    )

    def short_user_message(self, obj):
        return obj.user_message[:80]

    short_user_message.short_description = "User Message"
