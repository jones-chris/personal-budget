import React, { Component } from "react";


class Transaction extends Component {

	constructor(props) {
		super(props);

		this.state = {
			startDate: null,
			endDate: new Date()
		}
	}

	render() {
		return (
			<p hidden={this.props.hidden.toString() === 'true'}>Transactions!</p>
		)
	}

}

export default Transaction;