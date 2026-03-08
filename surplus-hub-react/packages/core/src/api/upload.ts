
import { apiClient, unwrapApiData } from "./client";

export interface UploadResponse {
    url: string;
}

export const uploadImage = async (file: File): Promise<string> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiClient.post("/api/v1/upload/image", formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });

    const data = unwrapApiData<UploadResponse>(response.data);
    return data.url;
};
