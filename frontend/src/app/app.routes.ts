import { Routes } from "@angular/router";

export const routes: Routes = [
	{
		path: "",
		loadComponent: () =>
			import("./pages/vending-machine/vending-machine").then(module => module.VendingMachinePage),
	},
	{ path: "**", redirectTo: "" },
];
