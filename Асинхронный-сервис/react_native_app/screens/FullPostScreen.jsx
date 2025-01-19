import React, {useEffect, useState} from 'react'
import styled from 'styled-components/native'
import {View, ScrollView} from "react-native";
import {Loading} from "@/components/Loader";
import axios from "axios";

const PostImage = styled.Image`
  border-radius: 10px;
  width: 100%;
  height: 350px;
  margin-bottom: 20px;
`

const PostDetails = styled.View`
  flex-direction: column;
  padding-bottom: 25px;
`

const PostText = styled.Text`
  flex-direction: column;
  font-size: 18px;
  line-height: 24px;
`

const FullPostScreen = ({ route, navigation }) => {

    const [isLoading, setIsLoading] = useState(true)
    const [data, setData] = useState()

    const { id, name } = route.params

    const fetchGroup = () => {
        navigation.setOptions({
            name,
        })

        axios
            .get(`http://${process.env.EXPO_PUBLIC_IP_ADDRESS}:8000/api/substances/` + id)
            .then(({data}) => {
                setData(data)
            })
            .catch((err) => {
                alert("Ошибка, не удалось получить статью")
            })
            .finally(() => {
                setIsLoading(false)
            })
    }

    useEffect(fetchGroup, [])

    if (isLoading) {
        return (
            <View style={{
                flex: 1,
                justifyContent: 'center',
                alignItems: 'center'
            }}>
                <Loading />
            </View>
        )
    }

    return (
        <ScrollView style={{ padding: 20 }}>
            <PostImage source={{uri: data.image}} />
            <PostDetails>
                <PostText>
                    Название: {data.name}
                </PostText>
                <PostText>
                    Описание: {data.description}
                </PostText>
                <PostText>
                    Порядковый номер: {data.number}
                </PostText>
            </PostDetails>
        </ScrollView>
    )
}

export default FullPostScreen;