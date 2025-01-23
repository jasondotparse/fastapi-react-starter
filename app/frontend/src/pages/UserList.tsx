import React, { useState, useEffect } from "react";
import axios from "../axiosConfig";
import AddUserModal from "./../components/AddUserModal"; // Import AddUserModal component

type User = {
  id: number;
  username: string;
  age: number;
};

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [showAddUserModal, setShowAddUserModal] = useState<boolean>(false);

  const fetchUsers = async () => {
    try {
      const response = await axios.get<User[]>("/user/all");
      setUsers(response.data);
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <div className="container mt-5">
      <h2 className="text-center mb-4">User List</h2>
      <button
        className="btn btn-primary mb-3"
        onClick={() => setShowAddUserModal(true)}
      >
        Add User
      </button>
      <table className="table table-bordered table-hover">
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Age</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.username}</td>
              <td>{user.age}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Add User Modal */}
      {showAddUserModal && (
        <AddUserModal
          onClose={() => setShowAddUserModal(false)}
          onUserAdded={fetchUsers}
        />
      )}
    </div>
  );
};

export default UserList;
