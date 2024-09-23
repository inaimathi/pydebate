import logging

from . import chat

logger = logging.getLogger("pydebate")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def _setup_speakers(debate_question):
    logging.info("_setup_speakers - setting up participants")
    perspectives = chat.generate_json(
        f"Given the question `{debate_question}`, what different perspectives should be taken into consideration when thinking about the answer? Return a response of type [String] in JSON format with no other commentary."
    )
    logging.info(f"_setup_speakers - prompts for {len(perspectives)} participants...")
    return [
        {
            "id": ix,
            "label": chat.generate(
                f"There is a debate about to happen. We need a label for someone taking the position of `{p}`. The label should be a phrase starting with 'Speaker for' and be no longer than five words. For instance, 'Speaker for thorns' or 'Speaker for the self' or 'Speaker for the southern hemisphere'. Return only the label and no other commentary."
            ),
            "perspective": p,
            "prompt": chat.generate(
                f"There is a debate about to happen. Given the position of `{p}`, write a prompt that would be suitable for giving an LLM in order to have it argue the position honestly, effectively and thoroughly. Return only the prompt and no other commentary."
            ),
        }
        for ix, p in enumerate(perspectives)
    ]


def system_prompt_from_speaker(debate_question, speaker):
    return f"""You are "{speaker['label']}". You are participating in a debate regarding the question "{debate_question}", and your position is "{speaker['perspective']}". {speaker['prompt']}"""


def _opening_statements(debate_question, speakers):
    return [
        {
            "speaker": s["label"],
            "content": chat.generate(
                f"{system_prompt_from_speaker(debate_question, s)}. You have one paragraph of between one and five sentences; please present your opening statement."
            ),
        }
        for s in speakers
    ]


def mk_debate(debate_question):
    speakers = _setup_speakers(debate_question)
    return {
        "question": debate_question,
        "speakers": speakers,
        "messages": _opening_statements(debate_question, speakers),
    }


def _transcript_of(debate):
    return "\n\n".join(
        f"{msg['speaker']}: {msg['content']}" for msg in debate["messages"]
    )


def judge_debate(debate):
    tscr = _transcript_of(debate)
    return {
        "answer": chat.generate(
            f"You are a judge. The lord of all the earth, with wisdom and understanding of all topics and matters of import. The question brought before you is '{debate['question']} '. Your court have debated. The debate went as follows: {tscr}. What is your answer to the question, provide no additional commentary."
        ),
        "summary": chat.generate(
            f"You are a judge. The lord of all the earth, with wisdom and understanding of all topics and matters of import. The question brought before you is '{debate['question']}'. Your court have debated. The debate went as follows: {tscr}. What is your best three sentence summary of the debate? Provide no additional commentary."
        ),
    }


def debate(debate_question):
    logging.info("debate - setting up")
    db = mk_debate(debate_question)
    logging.info("debate - speaking")
    # TODO - round robin, check if each speaker wants to respond. If so, ask for response, keep going for 3 rounds.
    # TODO - concluding statements
    logging.info("debate - judging")
    judgement = judge_debate(db)
    db["judgement"] = judgement
    return db
