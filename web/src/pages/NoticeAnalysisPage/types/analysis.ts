export type OcrLine = {
	text: string;
	confidence: number;
	x: number;
	y: number;
	width: number;
	height: number;
};
export type ExtractedField = {
	label: "Date" | "Amount" | "Phone";
	value: string;
	source_line: number;
	source_quote: string;
	confidence: number;
};
export const RISK_VALUES = [
	"routine",
	"money",
	"legal",
	"immigration",
	"medical",
	"threatening",
	"unreadable",
] as const;
export type Risk = (typeof RISK_VALUES)[number];

export type AnalysisResult = {
	risk: Risk;
	kind: string;
	lines: OcrLine[];
	fields: ExtractedField[];
	what_happened: string;
	action_needed: string;
	key_details: string;
	warning: string;
};
