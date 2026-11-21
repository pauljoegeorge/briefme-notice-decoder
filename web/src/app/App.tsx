import { Link, Route, Routes } from "react-router";
import { NoticeAnalysisPage } from "../pages/NoticeAnalysisPage/NoticeAnalysisPage";
import { AppShell } from "./AppShell";

export function App() {
	return (
		<Routes>
			<Route path="/" element={<AppShell />}>
				<Route index element={<NoticeAnalysisPage />} />
				<Route
					path="*"
					element={
						<p>
							Page not found. <Link to="/">Go home</Link>.
						</p>
					}
				/>
			</Route>
		</Routes>
	);
}
