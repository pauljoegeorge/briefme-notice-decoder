import { Outlet } from "react-router";
import "./AppShell.css";

export function AppShell() {
	return (
		<div className="shell">
			<header className="masthead">
				<div className="mark" aria-hidden="true">
					文
				</div>
				<div>
					<div className="eyebrow">LOCAL PROTOTYPE</div>
					<h1>Notice Decoder</h1>
				</div>
			</header>
			<main>
				<Outlet />
			</main>
		</div>
	);
}
