pragma solidity >=0.4.22 <0.6.0;
contract Tester {
    
    string message;
    function setMessage(string memory msge) public {
        message = msge;
    }
    
    function getMessage() public view returns (string memory) {
        return message;
    }

}