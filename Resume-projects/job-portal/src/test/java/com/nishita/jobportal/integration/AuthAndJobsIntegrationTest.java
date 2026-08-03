package com.nishita.jobportal.integration;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
@SpringBootTest(properties={"spring.datasource.url=jdbc:h2:mem:testdb;MODE=PostgreSQL;DB_CLOSE_DELAY=-1","spring.jpa.hibernate.ddl-auto=create-drop"}) @AutoConfigureMockMvc
class AuthAndJobsIntegrationTest{
 @Autowired MockMvc mvc;@Autowired ObjectMapper mapper;
 @Test void publicCanSearchSeededJobs()throws Exception{mvc.perform(get("/api/jobs").param("q","Java")).andExpect(status().isOk()).andExpect(jsonPath("$.content[0].title").value("Software Engineering Intern"));}
 @Test void candidateCanLoginAndReadApplications()throws Exception{String body=mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON).content("{\"email\":\"candidate@example.com\",\"password\":\"Password123!\"}")).andExpect(status().isOk()).andExpect(jsonPath("$.role").value("CANDIDATE")).andReturn().getResponse().getContentAsString();JsonNode json=mapper.readTree(body);mvc.perform(get("/api/candidate/applications").header("Authorization","Bearer "+json.get("token").asText())).andExpect(status().isOk()).andExpect(jsonPath("$.content").isArray());}
 @Test void recruiterEndpointRejectsCandidateRole()throws Exception{String body=mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON).content("{\"email\":\"candidate@example.com\",\"password\":\"Password123!\"}")).andReturn().getResponse().getContentAsString();String token=mapper.readTree(body).get("token").asText();mvc.perform(get("/api/recruiter/analytics").header("Authorization","Bearer "+token)).andExpect(status().isForbidden());}
}
