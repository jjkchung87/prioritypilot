import axios from "axios";

const BASE_URL = "http://127.0.0.1:5000/prioritypilot/api"

class UserApi {
  // the token for interactive with the API will be stored here.
  static token;
  
  // method to request any API route, returns response data
  static async request(endpoint, data = {}, method = "get") {
    const url = `${BASE_URL}/${endpoint}`;
    const headers = { Authorization: `Bearer ${UserApi.token}` };
    const params = (method === "get")
        ? data
        : {};
    try {
      return (await axios({ url, method, data, params, headers })).data;
    } catch (err) {
      console.error("API Error:", err.response);
      let message = err.response.data.msg;
      throw Array.isArray(message) ? message : [message];
    }
  }

  // Get the current user
  static async getCurrentUser(user_id) {
    let res = await this.request(`users/${user_id}`);
    return res;
  }

  // Signup for site, returns token, creates a new user in db.
  static async register(data) {
    let res = await this.request("users/signup", data, "post");
    return res.access_token;
  }

  // Login method, returns token 
  static async login(data) {
    let res = await this.request("users/login", data, "post");
    return res.access_token;
  }

  // Adds Project to DB
  static async addProject(data) {
    let res = await this.request("projects", data, "post");
    return res;
  }

  // Adds Task to DB
  static async addTask(data, project_id) {
    console.log(data)
    let res = await this.request(`projects/${project_id}/task`, data, "post");
    return res;
  }

  // Edit Task to DB
  static async editTask(data, project_id, task_id) {
    console.log('print new task', data)
    let res = await this.request(`projects/${project_id}/tasks/${task_id}`, data, "patch");
    return res;
  }

  // Delete Task by ID
  static async deleteTask(task_id) {
    console.log(task_id)
    let res = await this.request(`tasks/${task_id}`, task_id, "delete");
    return res;
  }

   // Get all tasks for user
   static async getUsersTasks(user_id) {
    let res = await this.request(`users/${user_id}/tasks`);
    return res;
  }

   // Get all tasks for project
   static async getProjectTasks(project_id) {
    let res = await this.request(`projects/${project_id}/tasks"`);
    return res;
  }

  // Get AI tips for task
  static async getAiTips(taskId) {
    console.log(taskId)
    let res = await this.request(`tasks/${taskId}/tip`, taskId, "post");
    console.log(res)
    return res.data;
  }

  // Get subordinates of user
  static async getSubs(userId) {
    let res = await this.request(`users/${userId}/subs`);
    return res
  }
  
  
  // Get users of project
  
  static async getUsersByProject(projectId) {
    try {
      let res = await this.request(`projects/${projectId}/users`);
      if (res) {
        return res;
      } else {
        console.error("API Error: Response data is undefined");
        return [];
      }
    } catch (error) {
      console.error("API Error:", error.message);
      return [];
    }
  }


 }

export default UserApi