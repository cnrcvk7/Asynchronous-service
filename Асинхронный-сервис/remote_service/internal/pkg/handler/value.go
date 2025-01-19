package handler

import (
	"bytes"
	"encoding/json"
	"fmt"
	"github.com/gin-gonic/gin"
	"math/rand"
	"net/http"
	"time"
)

type ValueRequest struct {
	AccessKey int64 `json:"access_key"`
	Value     int   `json:"value"`
}

type Request struct {
	OrderId int64 `json:"medicine_id"`
}

func (h *Handler) issueValue(c *gin.Context) {
	var input Request
	if err := c.BindJSON(&input); err != nil {
		newErrorResponse(c, http.StatusBadRequest, err.Error())
		return
	}
	fmt.Println("handler.issueValue:", input)

	c.Status(http.StatusOK)

	go func() {
		time.Sleep(3 * time.Second)
		sendValueRequest(input)
	}()
}

func sendValueRequest(request Request) {

	var value = -1
	if rand.Intn(10)%10 >= 3 {
		value = rand.Intn(4)
	}

	answer := ValueRequest{
		AccessKey: 123,
		Value:     value,
	}

	client := &http.Client{}

	jsonAnswer, _ := json.Marshal(answer)
	bodyReader := bytes.NewReader(jsonAnswer)

	requestURL := fmt.Sprintf("http://django:8000/api/medicines/%d/update_dose/", request.OrderId)

	req, _ := http.NewRequest(http.MethodPut, requestURL, bodyReader)

	req.Header.Set("Content-Type", "application/json")

	response, err := client.Do(req)
	if err != nil {
		fmt.Println("Error sending PUT request:", err)
		return
	}

	defer response.Body.Close()

	fmt.Println("Результат вычислений:", value)
	fmt.Println("PUT Request Status:", response.Status)
}
