import { useEffect, useRef, useState } from "react";
import { analyzeNotice } from "../api/analyzeNotice";
import type { AnalysisResult } from "../types/analysis";

type NoticeAnalysisController = {
	file: File | null;
	preview: string;
	analysis: AnalysisResult | null;
	activeLine: number | null;
	loading: boolean;
	error: string;
	selectFile: (file: File | null) => void;
	selectLine: (index: number) => void;
	readNotice: () => Promise<void>;
};

export function useNoticeAnalysis(): NoticeAnalysisController {
	const [file, setFile] = useState<File | null>(null);
	const [preview, setPreview] = useState("");
	const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
	const [activeLine, setActiveLine] = useState<number | null>(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const pending = useRef<AbortController | null>(null);

	useEffect(() => {
		if (!file) return;
		const url = URL.createObjectURL(file);
		setPreview(url);
		return () => URL.revokeObjectURL(url);
	}, [file]);

	useEffect(
		() => () => {
			pending.current?.abort();
			pending.current = null;
		},
		[],
	);

	function selectFile(nextFile: File | null) {
		pending.current?.abort();
		pending.current = null;
		setFile(nextFile);
		setPreview("");
		setAnalysis(null);
		setActiveLine(null);
		setLoading(false);
		setError("");
	}

	async function readNotice() {
		if (!file || pending.current) return;
		const controller = new AbortController();
		pending.current = controller;
		setError("");
		setAnalysis(null);
		setActiveLine(null);
		setLoading(true);
		try {
			const result = await analyzeNotice(file, controller.signal);
			if (pending.current === controller) setAnalysis(result);
		} catch (cause) {
			if (!controller.signal.aborted && pending.current === controller) {
				setError(cause instanceof Error ? cause.message : "Analysis failed.");
			}
		} finally {
			if (pending.current === controller) {
				pending.current = null;
				setLoading(false);
			}
		}
	}

	return {
		file,
		preview,
		analysis,
		activeLine,
		loading,
		error,
		selectFile,
		selectLine: setActiveLine,
		readNotice,
	};
}
