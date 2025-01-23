import axios from "axios";
import { Channel, NewChannel } from "@/types/channel";


const API_URL = 'http://89.104.68.234:8000/'// Подставляем значение из окружения, если оно есть

const axiosInstance = axios.create({
	baseURL: API_URL,
})

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token) {
    config.headers.Authorization = `Basic ${token}`;
  }
  return config;
});

axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("auth_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const channelsApi = {
	getAll: async () => {
		const response = await axiosInstance.get('/channels/get_all')
		return response.data.channels // Changed this line to access the channels array
	},

	getById: async (id: number) => {
		const response = await axiosInstance.get(`/channels/get/${id}`)
		return response.data
	},

	create: async (channel: NewChannel) => {
		const response = await axiosInstance.post('/channels/add', channel)
		return response.data
	},

	check: async (chat_id: number) => {
		const response = await axiosInstance.post(`/channels/check/${chat_id}`)
		return response.data
	},

	update: async (id: number, channel: NewChannel) => {
		const response = await axiosInstance.put(`/channels/update/${id}`, channel)
		return response.data
	},

	delete: async (id: number) => {
		const response = await axiosInstance.delete(`/channels/delete/${id}`)
		return response.data
	},

	toggleActive: async (id: number, active: boolean) => {
		const endpoint = active ? 'on' : 'off'
		const response = await axiosInstance.post(`/channels/${endpoint}/${id}`)
		return response.data
	},
}