from agents.base import PaperAgent

class SlideGeneratorAgent(PaperAgent):
    name = "Slide Generator Agent"
    task = "Create a polished, detailed 8–10 slide academic presentation grounded only in these excerpts. Return ONLY valid JSON in this exact shape: {\"slides\":[{\"title\":\"...\",\"bullets\":[\"...\",\"...\"],\"citation\":\"p. N\"}]}. Build a clear teaching narrative in this order: (1) title and central takeaway, (2) context, problem, and research gap, (3) objectives/questions and key concepts with brief definitions, (4) study design, data/sample, and measures, (5) method or analysis workflow step by step, (6) primary findings with exact reported numbers, units, and comparison baselines, (7) secondary findings and what they mean, (8) contributions and implications, (9) limitations/validity, (10) conclusion and takeaways. Combine adjacent sections only when the paper has little evidence. Give 4–6 substantive, self-contained bullets per content slide. Explain why each method or result matters, connect methods to findings, define specialized terms on first use, and cite page numbers on every slide. Preserve caveats and distinguish reported results from interpretation. Never invent data or claim significance unless the paper reports it. If evidence is absent, say so. No extra prose or markdown fences."
    k = 16

    def generate_slides(self, topic="Create a clear academic presentation"):
        return self.run(topic)
