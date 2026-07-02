import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function ExperimentStartPage() {
  const navigate = useNavigate();

  useEffect(() => {
    const startExperiment = async () => {
      try {
        const participantId = localStorage.getItem("participant_id");

        await api.post("complete-survey/", {
          participant_id: participantId,
          survey_type: "pre",
        });

        const condition = localStorage.getItem("condition");

        if (condition === "idea-generator") {
          navigate("/idea-generator");
        } else {
          navigate("/critical-evaluator");
        }
      } catch (error) {
        console.error(error);

        navigate("/");
      }
    };

    startExperiment();
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      Loading Experiment...
    </div>
  );
}

export default ExperimentStartPage;
