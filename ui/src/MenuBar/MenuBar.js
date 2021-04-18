import React, { Component } from "react";
import Navbar from "react-bootstrap/Navbar";
import Nav from "react-bootstrap/Nav";
import Transaction from "../Transaction/Transaction";

class MenuBar extends Component {

	constructor(props) {
		super(props);

		this.state = {
			home: {
				hidden: false
			},
			transactions: {
				hidden: true
			}
		}
	}

	onShowTransactionSection = () => {
		let newState = {...this.state};
		newState.home.hidden = true;
		newState.transactions.hidden = false;

		this.setState(newState)
	}

	render() {
		return (
			// <Navbar bg="light" expand="lg">
			//   <Navbar.Brand href="#home">React-Bootstrap</Navbar.Brand>
			//   <Navbar.Toggle aria-controls="basic-navbar-nav" />
			//   <Navbar.Collapse id="basic-navbar-nav">
			//     <Nav className="mr-auto">
			//       <Nav.Link href="#home">Home</Nav.Link>
			//       <Nav.Link href="#link">Link</Nav.Link>
			//     </Nav>
			//   </Navbar.Collapse>
			// </Navbar>
			<div>
				<Navbar bg="light" expand="lg">
	                <Navbar.Brand href="#">pb</Navbar.Brand>
	                <Navbar.Toggle aria-controls="basic-navbar-nav" />
	                <Navbar.Collapse id="basic-navbar-nav">
	                    <Nav className="mr-auto">
	                        <Nav.Link className={this.state.transactions.hidden ? "nav-item active" : "nav-item"}
	                                  onClick={this.onShowTransactionSection}
	                        >
	                            Transactions
	                        </Nav.Link>
	                    </Nav>


	{/*                    <Button variant="outline-secondary"
	                            onClick={this.props.onSaveQueryHandler}
	                    >
	                        Save Query
	                    </Button>*/}
	                </Navbar.Collapse>
	            </Navbar>

	            <Transaction
	            	hidden={this.state.transactions.hidden}
	            />
            </div>
    	)
	}

}

export default MenuBar;