import { Button, Card, Icon } from 'semantic-ui-react';
import { useState } from 'react';
import EditTaskForm from './EditTaskForm';
import UserApi from '../api';
import AiTipsModal from './AiTipsModal';


function TaskCard({ task, setTasks, tasks, deleteTask }) {
  const [showEditTask, setShowEditTask] = useState(false);
  const [currentStatus, setCurrentStatus] = useState(task.status);
  const [showAiModal, setShowAiModal] = useState(false);

  // Define the priority colors
  const priorityColors = {
    low: 'green',
    medium: 'yellow',
    high: 'red',
  };

  // Function to get the priority color
  const getPriorityColor = (priority) => priorityColors[priority.toLowerCase()];

  const updateStatus = async (status) => {
    let taskWithNewStatus = { ...task, status: status };
    await UserApi.editTask(taskWithNewStatus, task.project_id, task.id);
    let list = tasks.map((item) => {
      if (item.id === task.id) {
        item.status = status;
      }
      return item;
    });
    setTasks(list);
  }

  const addUpdates = async (data) => {
    await UserApi.editTask(data, task.project_id, task.id);
    let list = tasks.map((item) => {
      if (item.id === task.id) {
        item = data;
      }
      return item;
    });
    setTasks(list);
  }

  const handleDelete = async (id) => {
    await deleteTask(id);
  }

  return (
    <>
      {showAiModal && <AiTipsModal task={task} closeModal={() => setShowAiModal(false)} />}
      {showEditTask && <EditTaskForm task={task} addUpdates={addUpdates} setShowForm={setShowEditTask} tasks={tasks} />}
      <Card raised className='task-card'>
        <Card.Content>
          <div className='card-icons'>
            {currentStatus === "Not Started" && <Button size="tiny" onClick={() => updateStatus('In Progress')}>Start Task</Button>}
            {(currentStatus === "Not Started" || currentStatus === "In Progress") && <Button size="tiny" onClick={() => updateStatus('Complete')}>Complete Task</Button>}
            {currentStatus !== "Complete" && (
              <Button size="tiny" icon onClick={() => setShowEditTask(true)}><Icon name="edit" /></Button>
            )}
            <Button size="tiny" icon onClick={() => handleDelete(task.id)}><Icon name="delete" /></Button>
          </div>
          <Card.Header className='task-name'>{task.task_name}</Card.Header>
          <Card.Meta>
            <b>Priority:</b> {task.priority}
            <Icon name='circle' color={getPriorityColor(task.priority)} />
          </Card.Meta>
          <Card.Meta>
            <b>Deadline:</b> <span className={new Date(task.end_date)< new Date() ? 'past-due' : 'not-past-due'}>
              {new Date(task.end_date).toLocaleDateString('en-US')}
            </span>
            {new Date(task.end_date) < new Date() && <Icon color='red' name="exclamation circle" />}
          </Card.Meta>
          <div className='card-icons'>
            {currentStatus === "In Progress" && <> <Icon name="clock" color='green' className="in-progress-icon" />In Progress </>}
            {currentStatus === "Complete" && <> <Icon name="check circle" color='green' className='completed' />Completed </>}
          </div>
          <Card.Description><i>{task.description}</i></Card.Description>
          <Card.Meta></Card.Meta>
        </Card.Content>
        <Card.Content extra>
          <Button className="task-ai-button" size="tiny" onClick={() => setShowAiModal(true)}>Tips from PriorityPilot</Button>
          <span className='created-at'>Date created: {new Date(task.created_at).toLocaleDateString('en-US')}</span>
        </Card.Content>
      </Card>
    </>
  );
}

export default TaskCard;
