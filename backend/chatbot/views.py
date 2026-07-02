from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils import timezone
import time

from chatbot.services.llm import generate_response
from chatbot.services.knowledge import get_context
from chatbot.prompts import (
    IDEA_GENERATOR_PROMPT,
    CRITICAL_EVALUATOR_PROMPT
)
from django.db.models import Avg
from .models import (
    Participant,
    ChatSession,
    ChatMessage,
    ExperimentCondition,
    ExperimentPhase,
    Survey
)
import logging

logger = logging.getLogger(__name__)

@api_view(["GET"])
def health(request):
    return Response({
        "status": "working"
    })

@api_view(["POST"])
def start_experiment(request):

    # idea_count = Participant.objects.filter(
    #     assigned_condition__name="idea-generator"
    # ).count()

    # critical_count = Participant.objects.filter(
    #     assigned_condition__name="critical-evaluator"
    # ).count()

    # if idea_count <= critical_count:
    #     condition_name = "idea-generator"
    # else:
    #     condition_name = "critical-evaluator"

    # condition = ExperimentCondition.objects.get(
    #     name=condition_name
    # )

    # participant = Participant.objects.create(
    #     assigned_condition=condition
    # )

    logger.info("starting an experiment")

    ig_ce_count = Participant.objects.filter(
        role_order="IG_CE"
    ).count()

    ce_ig_count = Participant.objects.filter(
        role_order="CE_IG"
    ).count()

    if ig_ce_count <= ce_ig_count:
        role_order = "IG_CE"
    else:
        role_order = "CE_IG"

    participant = Participant.objects.create(
        role_order=role_order
    )

    idea_generator = ExperimentCondition.objects.get(
        name="idea-generator"
    )

    critical_evaluator = ExperimentCondition.objects.get(
        name="critical-evaluator"
    )

    if role_order == "IG_CE":
        first = idea_generator
        second = critical_evaluator
    else:
        first = critical_evaluator
        second = idea_generator

    phase1 = ExperimentPhase.objects.create(
        participant=participant,
        phase_number=1,
        condition=first,
    )

    phase2 = ExperimentPhase.objects.create(
        participant=participant,
        phase_number=2,
        condition=second,
    )

    Survey.objects.create(
        phase=phase1
    )

    Survey.objects.create(
        phase=phase2
    )

    return Response({
        "participant_id": str(participant.participant_id),
        "role_order": role_order,
        "current_phase": 1,
        "condition": first.name,
    })

@api_view(["POST"])
def complete_survey(request):

    participant_id = request.data.get(
        "participant_id"
    )
    phase_id = request.data.get(
        "phase_id"
    )

    try:

        participant = Participant.objects.get(
            participant_id=participant_id
        )

        phase = ExperimentPhase.objects.get(
            participant = participant,
            phase_number = phase_id
        )

        survey = Survey.objects.get(
            phase = phase
        )

        survey.completed = True
        survey.completed_at = timezone.now()
        survey.save()

    except survey.DoesNotExist:

        return Response(
            {
                "error":
                "survey not found"
            },
            status=404
        )
    
    
    phase.finished_at = timezone.now()
    phase.save()

    # If this was the second phase, the whole study is complete
    if phase.phase_number == 2:
        participant.finished_at = timezone.now()
        participant.save()

    return Response({
        "success": True
    })

@api_view(["GET"])
def chat_history(request, session_id):

    try:
        session = ChatSession.objects.get(
            session_id=session_id
        )

    except ChatSession.DoesNotExist:
        return Response(
            {"messages": []}
        )

    messages = ChatMessage.objects.filter(
        session=session
    ).order_by("created_at")

    data = []

    for msg in messages:

        data.append({
            "id": msg.id,
            "user_message": msg.user_message,
            "ai_response": msg.ai_response,
            "created_at": msg.created_at
        })

    return Response({
        "messages": data
    })

@api_view(["POST"])
def attentionPrediction(request):
    try:
        message = ChatMessage.objects.get(
            id=request.data.get("response_id")
        )
        logger.info("Chat message accessed: %s", message.id)
    except ChatMessage.DoesNotExist:
        logger.error(
            "Error accessing chatmessage: %s",
            request.data.get("response_id")
        )
        return Response(
            {
                "error": "Participant not found"
            },
            status=404
        )

    word_count = len(message.ai_response.split())
    avg_reading_speed = 200
    message.actual_engagement = request.data.get("actual_engagement")
    message.engagement_estimation = (word_count/avg_reading_speed) * 60
    message.predicted_engagement = request.data.get("predicted_engagement")
    message.predicted_reading_estimation = request.data.get("predicted_engagement")/message.engagement_estimation

    message.save()
    logger.info("chat message analytics updated: %s", message.id)
    return Response({"success": True})




@api_view(["POST"])
def chat(request):

    start_time = time.time()

    role = request.data.get("role")
    user_message = request.data.get("message")
    session_id = request.data.get("session_id")
    participant_id = request.data.get("participant_id")

    try:
        participant = Participant.objects.get(
            participant_id=participant_id
        )
    except Participant.DoesNotExist:
        return Response(
            {
                "error": "Participant not found"
            },
            status=404
        )
    
    condition, _ = ExperimentCondition.objects.get_or_create(
        name=role
    )

    phase = ExperimentPhase.objects.get(
                participant = participant,
                condition = condition
            )



    # if not participant.pre_survey_completed:
    #     return Response(
    #         {
    #             "error": "Complete survey first"
    #         },
    #         status=403
    #     )


    # condition, _ = ExperimentCondition.objects.get_or_create(
    #     name=role
    # )

    session, _ = ChatSession.objects.get_or_create(
        session_id=session_id,
        phase = phase
    )

    # Get last 20 messages for memory
    # previous_messages = (
    #     ChatMessage.objects
    #     .filter(session=session)
    #     .order_by("created_at")[:20]
    # )

    # Get all messages for memory
    previous_messages = (
        ChatMessage.objects
        .filter(session=session)
        .order_by("created_at")
    )

    # Retrieve relevant university context for this query
    context = get_context(user_message)

    base_prompt = IDEA_GENERATOR_PROMPT if role == "idea-generator" else CRITICAL_EVALUATOR_PROMPT

    if context:
        system_content = (
            f"{base_prompt}\n\n"
            f"=== University of Koblenz — FB4 Research Context ===\n"
            f"The following is real information about faculty, research projects, and thesis topics "
            f"at the University of Koblenz Computer Science department. "
            f"Use it to ground your suggestions in the department's actual research areas:\n\n"
            f"{context}\n"
            f"====================================================="
        )
    else:
        system_content = base_prompt

    messages = []
    messages.append({
        "role": "system",
        "content": system_content
    })

    # system_prompt = (
    #     IDEA_GENERATOR_PROMPT
    #     if role == "idea-generator"
    #     else CRITICAL_EVALUATOR_PROMPT
    # )

    # messages = [
    #     {
    #         "role": "system",
    #         "content": system_prompt
    #     }
    # ]

    # Add conversation history
    for msg in previous_messages:

        messages.append(
            {
                "role": "user",
                "content": msg.user_message
            }
        )

        messages.append(
            {
                "role": "assistant",
                "content": msg.ai_response
            }
        )

    # Add current user message
    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    ai_response = generate_response(
        messages
    )

    response_time_ms = int(
        (time.time() - start_time) * 1000
    )

    dataSaved  =ChatMessage.objects.create(
        session=session,
        role=role,
        user_message=user_message,
        ai_response=ai_response,
        response_time_ms=response_time_ms
    )

    session.total_messages += 1
    session.save()

    return Response({
        "response": ai_response,
        "response_id": dataSaved.id
    })


@api_view(["GET"])
def experiment_stats(request):

    return Response({

        "participants":
            Participant.objects.count(),

        "idea_generator":
            Participant.objects.filter(
                assigned_condition__name=
                "idea-generator"
            ).count(),

        "critical_evaluator":
            Participant.objects.filter(
                assigned_condition__name=
                "critical-evaluator"
            ).count(),

        "completed":
            Participant.objects.filter(
                post_survey_completed=True
            ).count()

    })


@api_view(["GET"])
def experiment_export(request):

    participants = Participant.objects.all()

    data = []

    for p in participants:

        data.append({

            "participant_id":
                str(p.participant_id),

            "condition":
                p.assigned_condition.name,

            "total_messages":
                ChatMessage.objects.filter(session__participant=p).count(),   

            "pre_completed":
                p.pre_survey_completed,

            "post_completed":
                p.post_survey_completed,

            "started_at":
                p.started_at,

            "finished_at":
                p.finished_at,

            "session_duration_seconds": 
                p.session_duration_seconds,
            
            "session_duration_minutes": 
                p.session_duration_minutes,    
        })

    return Response(data)

@api_view(["GET"])
def chat_export(request):

    data = []

    messages = ChatMessage.objects.select_related(
        "session",
        "session__participant",
        "session__condition"
    )

    for index, msg in enumerate(messages, start=1):

        data.append({

            "participant_id":
                str(
                    msg.session.participant.participant_id
                ),

            "condition":
                msg.session.condition.name,

            "user_message":
                msg.user_message,

            "ai_response":
                msg.ai_response,

            "response_time_ms":
                msg.response_time_ms,

            "created_at":
                msg.created_at,

            "session_id":
                str(msg.session.session_id),

            "message_number": index,

            "total_messages":
                msg.session.total_messages,    

            "session_duration_seconds":
                msg.session.participant.session_duration_seconds,

            "session_duration_minutes":
                msg.session.participant.session_duration_minutes,

            "pre_completed":
                msg.session.participant.pre_survey_completed,

            "post_completed":
                msg.session.participant.post_survey_completed,    
        })

    return Response(data)

@api_view(["GET"])
def dashboard_data(request):

    participants = Participant.objects.count()

    completed = Participant.objects.filter(
        post_survey_completed=True
    ).count()

    idea_generator = Participant.objects.filter(
        assigned_condition__name="idea-generator"
    ).count()

    critical_evaluator = Participant.objects.filter(
        assigned_condition__name="critical-evaluator"
    ).count()

    completed_participants = Participant.objects.filter(
        finished_at__isnull=False
    )

    durations = [
        p.session_duration_minutes
        for p in completed_participants
        if p.session_duration_minutes is not None
    ]

    avg_duration = (
        round(sum(durations) / len(durations), 2)
        if durations
        else 0
    )

    avg_messages = ChatSession.objects.aggregate(
        Avg("total_messages")
    )["total_messages__avg"] or 0

    return Response({
        "participants": participants,
        "completed": completed,
        "idea_generator": idea_generator,
        "critical_evaluator": critical_evaluator,
        "avg_duration": avg_duration,
        "avg_messages": round(avg_messages, 2),
    })