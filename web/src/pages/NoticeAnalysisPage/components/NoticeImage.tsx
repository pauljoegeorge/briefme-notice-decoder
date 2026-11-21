import type { OcrLine } from "../types/analysis";

type Props = {
	preview: string;
	lines: OcrLine[];
	activeLine: number | null;
	onSelectLine: (index: number) => void;
};

export function NoticeImage({
	preview,
	lines,
	activeLine,
	onSelectLine,
}: Props) {
	const selected = activeLine === null ? null : lines[activeLine];
	return (
		<section className="photo-panel" aria-label="Original notice">
			<div className="section-head">
				<h2>Original notice</h2>
				<span>{lines.length} OCR lines</span>
			</div>
			<div className="photo-wrap">
				<img src={preview} alt="Uploaded original notice" />
				{lines.map((line, index) => (
					<button
						key={`${line.text}-${line.x}-${line.y}-${line.width}-${line.height}`}
						type="button"
						className={`highlight ${activeLine === index ? "active" : ""}`}
						style={{
							left: `${line.x * 100}%`,
							top: `${line.y * 100}%`,
							width: `${line.width * 100}%`,
							height: `${line.height * 100}%`,
						}}
						onClick={() => onSelectLine(index)}
						aria-label={`OCR line ${index + 1}: ${line.text}`}
					/>
				))}
			</div>
			{selected && (
				<div className="source">
					<span>Selected text</span>
					<strong>{selected.text}</strong>
					<small>OCR confidence {Math.round(selected.confidence * 100)}%</small>
				</div>
			)}
		</section>
	);
}
