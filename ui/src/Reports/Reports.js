import React, { Component } from "react";
import Button from "react-bootstrap/Button";


class Reports extends Component {


	constructor(props) {
		super(props);

		this.state = {
			startDate: null,
			endDate: null,
			report: null,
			reports: [],
			initialized: false
		};
	}

	getReports = () => {
		fetch(
			'http://localhost:5000/reports'
		).then(response => response.json())
		.then(responseJson => {
			let newState = {...this.state};
			newState.reports = responseJson;
			this.setState(newState);
		})
	}

	getReport = () => {
		// todo:  parameterize the report name from the API config.
		fetch(
            `http://localhost:5000/report/${this.state.report}?startDate=${this.state.startDate}&endDate=${this.state.endDate}`
		).then(response => response.blob())
		 .then(blob => {
			const file = window.URL.createObjectURL(blob);
    		window.location.assign(file);
		 })
	}

	render() {
		if (!this.props.hidden) {
			if (!this.state.initialized) {
				this.getReports();
				this.setState({...this.state, initialized: true});
			}
		}

		let reportOptionsJsx = [];
		// Default empty option.
		reportOptionsJsx.push(
			<option selected></option>
		);
		this.state.reports.forEach(report => {
			reportOptionsJsx.push(
				<option value={report.name}>{report.name}</option>
			);
		})

		return (
			<div hidden={this.props.hidden.toString() === 'true'}>
				<span>
					<label for="report"
					>
						Report
					</label>
					<select id="report"
 							onChange={(event) => this.setState({...this.state, report: event.target.value})}
					>
						{reportOptionsJsx}
					</select>

					<label for="fromDate"
					       className="dates-item"
					>
						From
					</label>
					<input type="date" 
						   id="fromDate"
						   onChange={(event) => this.setState({...this.state, startDate: event.target.value})}
				    >
				    </input>

					<label for="toDate" 
					       className="dates-item"
			        >
			        	To
			        </label>
					<input type="date" 
						   id="toDate"
						   onChange={(event) => this.setState({...this.state, endDate: event.target.value})}
				    >
				    </input>

					<Button variant="outline-primary"
					        className="dates-item"
							onClick={this.getReport}
					>
						Search
					</Button>
				</span>
			</div>
		);
	}

}

export default Reports;