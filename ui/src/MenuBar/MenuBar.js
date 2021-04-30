import React, { Component } from "react";
import Navbar from "react-bootstrap/Navbar";
import Nav from "react-bootstrap/Nav";

class MenuBar extends Component {

	constructor(props) {
		super(props);
	}

	onShowTransactionSection = () => {
		let newState = {...this.props.state};
		newState.home.hidden = true;
		newState.categories.hidden = true;
		newState.transactions.hidden = false;
		newState.reports.hidden = true;

		this.props.setStateFunc(newState);
	}

	onShowCategorySection = () => {
		let newState = {...this.props.state};
		newState.home.hidden = true;
		newState.categories.hidden = false;
		newState.transactions.hidden = true;
		newState.reports.hidden = true;

		this.props.setStateFunc(newState);
	}

	onShowReportsSection = () => {
		let newState = {...this.props.state};
		newState.home.hidden = true;
		newState.categories.hidden = true;
		newState.transactions.hidden = true;
		newState.reports.hidden = false;

		this.props.setStateFunc(newState);
	}

	render() {
		return (
			<div>
				<Navbar bg="light" expand="lg">
	                <Navbar.Brand href="#">pb</Navbar.Brand>
	                <Navbar.Toggle aria-controls="basic-navbar-nav" />
	                <Navbar.Collapse id="basic-navbar-nav">
	                    <Nav className="mr-auto">
	                        <Nav.Link className={this.props.state.transactions.hidden ? "nav-item" : "nav-item active"}
	                                  onClick={this.onShowTransactionSection}
	                        >
	                            Transactions
	                        </Nav.Link>
	                        <Nav.Link className={this.props.state.categories.hidden ? "nav-item": "nav-item active"}
	                                  onClick={this.onShowCategorySection}
	                        >
	                            Categories
	                        </Nav.Link>

	                        <Nav.Link className={this.props.state.reports.hidden ? "nav-item": "nav-item active"}
	                                  onClick={this.onShowReportsSection}
	                        >
	                            Reports
	                        </Nav.Link>
	                    </Nav>


	{/*                    <Button variant="outline-secondary"
	                            onClick={this.props.onSaveQueryHandler}
	                    >
	                        Save Query
	                    </Button>*/}
	                </Navbar.Collapse>
	            </Navbar>
            </div>
    	)
	}

}

export default MenuBar;