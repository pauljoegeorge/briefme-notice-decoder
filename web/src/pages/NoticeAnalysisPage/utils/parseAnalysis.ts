import {
	type AnalysisResult,
	type ExtractedField,
	type OcrLine,
	RISK_VALUES,
} from "../types/analysis";

function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isUnit(value: unknown): value is number {
	return (
		typeof value === "number" &&
		Number.isFinite(value) &&
		value >= 0 &&
		value <= 1
	);
}

function isLine(value: unknown): value is OcrLine {
	return (
		isRecord(value) &&
		typeof value.text === "string" &&
		isUnit(value.confidence) &&
		isUnit(value.x) &&
		isUnit(value.y) &&
		isUnit(value.width) &&
		isUnit(value.height)
	);
}

function isField(value: unknown, lines: OcrLine[]): value is ExtractedField {
	if (!isRecord(value)) return false;
	const source = value.source_line;
	return (
		(value.label === "Date" ||
			value.label === "Amount" ||
			value.label === "Phone") &&
		typeof value.value === "string" &&
		typeof value.source_quote === "string" &&
		value.source_quote.length > 0 &&
		isUnit(value.confidence) &&
		typeof source === "number" &&
		Number.isInteger(source) &&
		source >= 0 &&
		source < lines.length &&
		lines[source].text.includes(value.source_quote)
	);
}

export function parseAnalysis(value: unknown): AnalysisResult {
	if (
		!isRecord(value) ||
		!Array.isArray(value.lines) ||
		!value.lines.every(isLine)
	) {
		throw new Error(
			"The server returned an invalid analysis. Please try again.",
		);
	}
	const lines: OcrLine[] = value.lines;
	const strings = [
		"kind",
		"what_happened",
		"action_needed",
		"key_details",
		"warning",
	];
	if (
		!RISK_VALUES.some((risk) => risk === value.risk) ||
		!strings.every((key) => typeof value[key] === "string") ||
		!Array.isArray(value.fields) ||
		!value.fields.every((field: unknown) => isField(field, lines))
	) {
		throw new Error(
			"The server returned an invalid analysis. Please try again.",
		);
	}
	return value as AnalysisResult;
}
