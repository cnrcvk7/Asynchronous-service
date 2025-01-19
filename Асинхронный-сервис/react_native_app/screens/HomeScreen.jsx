import { FlatList, RefreshControl, TouchableOpacity} from 'react-native';
import Post from "../components/Post";
import React, {useEffect, useState} from "react";
import SearchBar from "../components/SearchBar";
import styled from 'styled-components/native';
import axios from "axios";

const HomeScreen =({ navigation }) => {

    const [isLoading, setIsLoading] = useState(true)
    const [items, setItems] = useState([])
    const [substance_name, setSubstanceName] = useState("")
    const [clicked, setClicked] = useState(false)

    const fetchPosts = () => {
        setIsLoading(true)
        axios
            .get(`http://${process.env.EXPO_PUBLIC_IP_ADDRESS}:8000/api/substances?substance_name=${substance_name}`)
            .then(({data}) => {
                setItems(data["substances"])
            })
            .catch((err) => {
                alert(err)
            })
            .finally(() => {
                setIsLoading(false)
            })
    }

    useEffect(fetchPosts, [substance_name])

    const renderItem = ({ item }) => (
        <TouchableOpacity onPress={() => navigation.navigate("FullPost", {id: item.id, name: item.name })}>
            <Post navigation={navigation} id={item.id} name={item.name} item={item} />
        </TouchableOpacity>
    )

    return (
        <PostsListContainer>

            <SearchBar searchPhrase={substance_name} setSearchPhrase={setSubstanceName} clicked={clicked} setClicked={setClicked} />

            <FlatList
                refreshControl={<RefreshControl refreshing={isLoading} onRefresh={fetchPosts} />}
                data={items}
                renderItem={renderItem}
            />

        </PostsListContainer>
    );
}

const PostsListContainer = styled.View`
  padding-bottom: 75px;
`

export default HomeScreen;
