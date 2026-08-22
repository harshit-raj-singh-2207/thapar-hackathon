import storage from '../storage/asyncStorage';
import { BASE_URL } from '../../constants/config';

class ApiClient {
  async getHeaders() {
    const token = await storage.getItem('userToken');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }

  async request(method, endpoint, options = {}) {
    const url = `${BASE_URL}${endpoint}`;
    const headers = await this.getHeaders();
    try {
      if (__DEV__) {
        console.log(`[API Request] ${method} ${url}`);
      }
      const response = await fetch(url, {
        method,
        headers,
        ...options,
      });
      return await this.handleResponse(response, url, method);
    } catch (err) {
      if (__DEV__) {
        console.error(`[API Fetch Error] ${method} ${url}:`, err.message || err);
      }
      if (err.name === 'TypeError' && (err.message.includes('fetch') || err.message.includes('Network'))) {
        const netErr = new Error(`Network Error: Unable to connect to backend at ${BASE_URL}. Ensure FastAPI backend is running and reachable.`);
        netErr.status = 0;
        throw netErr;
      }
      throw err;
    }
  }

  async get(endpoint) {
    return this.request('GET', endpoint);
  }

  async post(endpoint, data) {
    return this.request('POST', endpoint, {
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data) {
    return this.request('PUT', endpoint, {
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request('DELETE', endpoint);
  }

  async uploadMedia(endpoint, formData) {
    const url = `${BASE_URL}${endpoint}`;
    const token = await storage.getItem('userToken');
    try {
      if (__DEV__) {
        console.log(`[API Upload Request] POST ${url}`);
      }
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: formData,
      });
      return await this.handleResponse(response, url, 'POST');
    } catch (err) {
      if (__DEV__) {
        console.error(`[API Upload Error] POST ${url}:`, err.message || err);
      }
      throw err;
    }
  }

  async handleResponse(response, url, method) {
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (__DEV__) {
        console.error(`[API Error Response] ${method} ${url} - Status ${response.status}:`, data);
      }
      const error = new Error(data.detail || `API request failed with status ${response.status}`);
      error.status = response.status;
      error.detail = data.detail;
      throw error;
    }
    return data;
  }
}

export default new ApiClient();

