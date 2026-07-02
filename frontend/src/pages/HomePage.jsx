import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import universityLogo from "../assets/uk.svg";
import api from "../services/api";

function HomePage({ darkMode, setDarkMode }) {
  const navigate = useNavigate();
  useEffect(() => {
    document.title = "Generative AI Research Lab";
  }, []);

  const startExperiment = async () => {
    try {
      const res = await api.post("start-experiment/");

      localStorage.setItem("participant_id", res.data.participant_id);
      localStorage.setItem("role_order", res.data.role_order);
      localStorage.setItem("condition", res.data.condition);
      
      // note for nikhil : you can check from role_order to which 
      // survey to go after the chat with bot, IG_CE means 
      // first idea-generator then critical-evaluator
      // and CE_IG means the reverse

      const participantId = res.data.participant_id;

      window.location.href = `https://sosci.rlp.net/nikhil/?r=${res.data.participant_id}`;
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div
      className={`min-h-screen overflow-x-hidden transition-colors duration-300 ${
        darkMode ? "dark-scrollbar" : "light-scrollbar"
      } ${darkMode ? "bg-[#0B1020] text-white" : "bg-white text-black"}`}
    >
      {/* Header */}
      <header className="border-b border-red-500/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 md:px-6 py-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3 md:gap-4">
            <img
              src={universityLogo}
              alt="UK Logo"
              className="h-12 md:h-16 w-auto cursor-pointer transition duration-300 hover:scale-105"
              onClick={() => {
                window.location.href = "/";
              }}
            />

            <div>
              <h1
                className={`font-bold text-lg md:text-2xl ${
                  darkMode ? "text-white" : "text-black"
                }`}
              >
                Generative AI Research Lab
              </h1>

              <p
                className={`text-sm ${
                  darkMode ? "text-red-500" : "text-red-600"
                }`}
              >
                University of Koblenz
              </p>
            </div>
          </div>

          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`px-4 py-2 rounded-full border transition ${
              darkMode
                ? "bg-[#141B34] border-gray-700 hover:border-red-500"
                : "bg-white border-red-200 hover:border-red-500"
            }`}
          >
            {darkMode ? "☀️" : "🌙"}
          </button>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-4 md:px-6 pt-6 md: pb-12 text-center">
        <h2 className="font-bold leading-tight mb-6 text-4xl sm:text-5xl lg:text-6xl">
          AI Support for
          <span className="text-red-600 block md:inline"> Creative Tasks </span>
          in Thesis Topic Development
        </h2>

        <p
          className={`max-w-3xl mx-auto text-base md:text-lg lg:text-xl leading-relaxed ${
            darkMode ? "text-gray-300" : "text-gray-700"
          }`}
        >
          Explore how different AI roles influence creativity, brainstorming,
          and critical thinking during thesis topic generation and evaluation.
        </p>
      </section>

      <section className="max-w-6xl mx-auto px-4 md:px-6 pb-16">
        <div
          className={`rounded-3xl border p-10 text-center shadow-xl ${
            darkMode
              ? "bg-[#141B34] border-gray-800"
              : "bg-white border-red-200"
          }`}
        >
          <h3 className="text-3xl font-bold mb-6">Start Research Experiment</h3>

          <p className={`mb-8 ${darkMode ? "text-gray-300" : "text-gray-700"}`}>
            You will complete a short survey, interact with an AI assistant, and
            complete a final survey.
          </p>

          <button
            onClick={startExperiment}
            className="
        bg-red-600
        hover:bg-red-700
        text-white
        px-8
        py-4
        rounded-xl
        font-semibold
        transition
      "
          >
            Start Experiment
          </button>
        </div>
      </section>
    </div>
  );
}

export default HomePage;
