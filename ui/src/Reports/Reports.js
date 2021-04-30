import React, { Component } from "react";
import Button from "react-bootstrap/Button";


class Reports extends Component {


	constructor(props) {
		super(props);

		this.state = {
			startDate: null,
			endDate: null,
			report: null
		};
	}

	getReport = () => {
		// todo:  parameterize the report name from the API config.
		fetch(
            `http://localhost:5000/report/budget-to-variance-report?startDate=${this.state.startDate}&endDate=${this.state.endDate}`
		).then(response => response.blob())
		 .then(blob => {
			const file = window.URL.createObjectURL(blob);
    		window.location.assign(file);
		 })
	}

	render() {
		return (
			<div hidden={this.props.hidden.toString() === 'true'}>
				{/*<input type="date" 
					   id="fromDate"
					   onChange={(event) => this.setState({...this.state, startDate: event.target.value})}
			    >
				</input>*/}

				<span>
					<label for="report"
					>
						Report
					</label>
					<select id="report"
 							onChange={(event) => this.setState({...this.state, report: event.target.value})}
					>
						<option selected></option>
						<option value="budget-to-variance-report">Budget-to-Variance Report</option>
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