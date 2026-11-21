import type { ChangeEvent, FormEvent } from "react";

type Props = {
	file: File | null;
	loading: boolean;
	onFileChange: (file: File | null) => void;
	onSubmit: () => void;
};

export function UploadForm({ file, loading, onFileChange, onSubmit }: Props) {
	function selectFile(event: ChangeEvent<HTMLInputElement>) {
		onFileChange(event.target.files?.[0] ?? null);
	}

	function submit(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		onSubmit();
	}

	return (
		<form className="upload" onSubmit={submit} aria-busy={loading}>
			<label className="file-label" htmlFor="notice-file">
				<span className="upload-icon" aria-hidden="true">
					↑
				</span>
				<span>{file ? file.name : "Choose or take a notice photo"}</span>
				<small>JPEG, PNG, or WebP · up to 15 MB</small>
			</label>
			<input
				id="notice-file"
				type="file"
				accept="image/jpeg,image/png,image/webp"
				capture="environment"
				onChange={selectFile}
			/>
			<button disabled={!file || loading} type="submit">
				{loading ? "Reading notice…" : "Read notice"}
			</button>
		</form>
	);
}
