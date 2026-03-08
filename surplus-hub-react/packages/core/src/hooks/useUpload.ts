
import { useMutation, UseMutationResult } from "@tanstack/react-query";
import { apiClient, unwrapApiData } from "../api/client";

interface UploadResponse {
    url: string;
}

const uploadImageApi = async (file: File): Promise<string> => {
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

export const useUploadImage = (): UseMutationResult<string, Error, File> => {
    return useMutation({
        mutationFn: (file: File) => uploadImageApi(file),
    });
};
