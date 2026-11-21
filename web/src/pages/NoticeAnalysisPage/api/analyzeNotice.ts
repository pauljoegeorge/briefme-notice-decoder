import type { AnalysisResult } from "../types/analysis";
import { parseAnalysis } from "../utils/parseAnalysis";

export async function analyzeNotice(
	file: File,
	signal?: AbortSignal,
): Promise<AnalysisResult> {
	const form = new FormData();
	form.append("file", file);
	const response = await fetch("/api/notice-analyses", {
		method: "POST",
		body: form,
		signal,
	});
	if (!response.ok) {
		const body: unknown = await response.json().catch(() => ({}));
		const detail =
			typeof body === "object" &&
			body !== null &&
			"detail" in body &&
			typeof body.detail === "string"
				? body.detail
				: null;
		throw new Error(detail || `Analysis failed (${response.status}).`);
	}
	return parseAnalysis(await response.json().catch(() => null));
}
