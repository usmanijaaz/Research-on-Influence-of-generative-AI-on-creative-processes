from django.db import models
import uuid


class ExperimentCondition(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Participant(models.Model):

    participant_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    # assigned_condition = models.ForeignKey(
    #     ExperimentCondition,
    #     on_delete=models.CASCADE,
    #     related_name="participants"
    # )

    # Randomized order
    role_order = models.CharField(
        max_length=30,
        choices=[
            ("IG_CE", "Idea Generator → Critical Evaluator"),
            ("CE_IG", "Critical Evaluator → Idea Generator"),
        ]
    )

    started_at = models.DateTimeField(
        auto_now_add=True
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return str(self.participant_id)

    @property
    def session_duration_seconds(self):
        if not self.finished_at:
            return None

        return int(
            (self.finished_at - self.started_at).total_seconds()
        )

    @property
    def session_duration_minutes(self):
        if self.session_duration_seconds is None:
            return None

        return round(
            self.session_duration_seconds / 60,
            2
        )

class ExperimentPhase(models.Model):

    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="phases"
    )

    phase_number = models.IntegerField()

    condition = models.ForeignKey(
        ExperimentCondition,
        on_delete=models.CASCADE
    )

    survey_completed = models.BooleanField(default=False)

    started_at = models.DateTimeField(auto_now_add=True)

    finished_at = models.DateTimeField(
        null=True,
        blank=True
    )

class ChatSession(models.Model):

    # participant = models.ForeignKey(
    #     Participant,
    #     on_delete=models.CASCADE,
    #     related_name="sessions",
    #     null=True,
    #     blank=True
    # )

    phase = models.OneToOneField(
        ExperimentPhase,
        on_delete=models.CASCADE,
        related_name="chat_session"
    )

    session_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    # condition = models.ForeignKey(
    #     ExperimentCondition,
    #     on_delete=models.CASCADE
    # )

    total_messages = models.IntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return str(self.session_id)

class ChatMessage(models.Model):
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(
        max_length=30
    )

    user_message = models.TextField()

    ai_response = models.TextField()

    engagement_estimation = models.FloatField(default=0.0)
    actual_engagement = models.FloatField(default=0.0)
    predicted_engagement = models.FloatField(default=0.0)
    predicted_reading_estimation = models.FloatField(default=0.0)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    response_time_ms = models.IntegerField(
        default=0
    )

    def __str__(self):
        return f"Message {self.id}"
    
   
class Survey(models.Model):

    phase = models.OneToOneField(
        ExperimentPhase,
        on_delete=models.CASCADE,
        related_name="survey"
    )

    completed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )