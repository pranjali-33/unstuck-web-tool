// api/unstuck.js
// Unstuck (Clarity) — turns messy input into structured clarity.
// Branded method: The Real Ask -> The Core Pieces -> The So-What.
// Energy state controls DEPTH of output (Cognitive Load Theory:
// match output complexity to the user's current cognitive capacity).

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { dump, energy } = req.body || {};

  if (!dump || typeof dump !== 'string' || dump.trim().length < 3) {
    return res.status(400).json({ error: 'Paste something messy first and I will untangle it.' });
  }

  const depthRules = {
    Fried:
      "The user is severely depleted. Return ONLY 'the_real_ask' as a single clear sentence. Set 'core_pieces' to an empty array and 'so_what' to an empty string. Minimum cognitive load.",
    Drained:
      "The user is low on capacity. Return 'the_real_ask' (one sentence) and 2-3 short 'core_pieces'. Set 'so_what' to an empty string.",
    Charging:
      "The user has moderate capacity. Return the full structure: 'the_real_ask' (one sentence), 3-5 'core_pieces', and a one-sentence 'so_what'.",
    Charged:
      "The user has high capacity and is ready to act. Return the full structure plus a concrete suggested next step folded into 'so_what' (so_what = the implication AND the recommended move, two sentences max)."
  };

  const rule = depthRules[energy] || depthRules['Charging'];

  const systemPrompt =
    "You are Unstuck, a clarity engine that turns messy, unstructured input (rambling emails, tangled notes, " +
    "confusing messages) into clean structure using a consistent method: The Real Ask, The Core Pieces, and The So-What. " +
    "You apply MECE thinking: the core pieces must be distinct and non-overlapping. You are warm, sharp, and concise, " +
    "never robotic. You never use em dashes. You extract; you do not pad. If the input contains no real request, " +
    "make 'the_real_ask' describe the central point or message instead.";

  const userPrompt =
    "Here is the messy input:\n\"\"\"\n" + dump + "\n\"\"\"\n\n" +
    "User's current capacity state: " + energy + ".\n" +
    "Depth rule you MUST follow: " + rule + "\n\n" +
    "Respond ONLY with valid JSON, no markdown, no backticks, in exactly this shape:\n" +
    "{\"the_real_ask\": \"<the single real request or central point, one clear sentence>\", " +
    "\"core_pieces\": [\"<distinct key point>\", \"...\"], " +
    "\"so_what\": \"<the implication, or implication plus suggested next step per the depth rule>\"}";

  try {
    const groqRes = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + process.env.GROQ_API_KEY
      },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        temperature: 0.5,
        max_tokens: 500,
        response_format: { type: 'json_object' },
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ]
      })
    });

    if (!groqRes.ok) {
      const detail = await groqRes.text();
      console.error('Groq error:', detail);
      return res.status(502).json({ error: 'The engine had trouble. Please try once more.' });
    }

    const data = await groqRes.json();
    const raw = data.choices && data.choices[0] && data.choices[0].message ? data.choices[0].message.content : '';

    let parsed;
    try {
      parsed = JSON.parse(raw);
    } catch (e) {
      const cleaned = raw.replace(/```json|```/g, '').trim();
      parsed = JSON.parse(cleaned);
    }

    if (!parsed.the_real_ask) {
      throw new Error('Incomplete response');
    }

    return res.status(200).json({
      the_real_ask: parsed.the_real_ask,
      core_pieces: Array.isArray(parsed.core_pieces) ? parsed.core_pieces : [],
      so_what: parsed.so_what || ''
    });
  } catch (err) {
    console.error('Handler error:', err);
    return res.status(500).json({ error: 'Something slipped. Please try again in a moment.' });
  }
}
