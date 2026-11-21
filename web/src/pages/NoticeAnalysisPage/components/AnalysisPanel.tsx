import type { AnalysisResult } from "../types/analysis";

type Props = {
	analysis: AnalysisResult;
	activeLine: number | null;
	onSelectLine: (index: number) => void;
};

const CARDS = [
	["01", "What happened", "what_happened"],
	["02", "Do I need to act?", "action_needed"],
	["03", "Key details", "key_details"],
] as const;

export function AnalysisPanel({ analysis, activeLine, onSelectLine }: Props) {
	return (
		<section className="answer-panel" aria-label="Preliminary reading">
			<div className="section-head">
				<h2>Preliminary reading</h2>
				<span className={`risk ${analysis.risk}`}>{analysis.risk}</span>
			</div>
			<p className="warning">{analysis.warning}</p>
			{CARDS.map(([number, title, key]) => (
				<div className="answer-card" key={key}>
					<div className="card-number">{number}</div>
					<div>
						<h3>{title}</h3>
						<p>{analysis[key]}</p>
					</div>
				</div>
			))}
			<div className="fields">
				<h3>Details linked to the photo</h3>
				{analysis.fields.length === 0 && (
					<p>No dates, amounts, or phone numbers found.</p>
				)}
				{analysis.fields.map((field) => (
					<button
						key={`${field.label}-${field.value}-${field.source_line}-${field.source_quote}`}
						type="button"
						className={`field ${activeLine === field.source_line ? "active" : ""}`}
						onClick={() => onSelectLine(field.source_line)}
					>
						<span>{field.label}</span>
						<strong>{field.value}</strong>
						<small>Show source ↗</small>
					</button>
				))}
			</div>
		</section>
	);
}
