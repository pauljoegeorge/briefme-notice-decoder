import { AnalysisPanel } from "./components/AnalysisPanel";
import { NoticeImage } from "./components/NoticeImage";
import { UploadForm } from "./components/UploadForm";
import { useNoticeAnalysis } from "./hooks/useNoticeAnalysis";
import "./styles/page.css";
import "./styles/upload.css";
import "./styles/result.css";

export function NoticeAnalysisPage() {
	const notice = useNoticeAnalysis();

	return (
		<>
			<p className="intro">
				Understand a Japanese notice while keeping the original in view. This
				early version uses local OCR and simple rules; verify every detail
				yourself.
			</p>
			<UploadForm
				file={notice.file}
				loading={notice.loading}
				onFileChange={notice.selectFile}
				onSubmit={notice.readNotice}
			/>
			{notice.error && (
				<p className="error" role="alert">
					{notice.error}
				</p>
			)}
			{notice.analysis && (
				<div className="results">
					<NoticeImage
						preview={notice.preview}
						lines={notice.analysis.lines}
						activeLine={notice.activeLine}
						onSelectLine={notice.selectLine}
					/>
					<AnalysisPanel
						analysis={notice.analysis}
						activeLine={notice.activeLine}
						onSelectLine={notice.selectLine}
					/>
				</div>
			)}
			{!notice.analysis && notice.preview && (
				<div className="preview-only">
					<img src={notice.preview} alt="Selected notice for OCR" />
				</div>
			)}
			<footer className="prototype-note">
				No notice is saved by this prototype. Informational only; OCR and
				summaries may contain errors.
			</footer>
		</>
	);
}
