package com.nishita.jobportal.service;
import com.fasterxml.jackson.databind.JsonNode;
import com.nishita.jobportal.dto.ExternalJobResponse;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.HtmlUtils;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import java.time.*;
import java.util.*;
@Service public class ExternalJobService {
 private static final String FEED_URL="https://remotive.com/api/remote-jobs?limit=50";
 private final RestClient client;
 private volatile List<ExternalJobResponse> cached=List.of(); private volatile Instant cacheExpires=Instant.EPOCH;
 public ExternalJobService(){SimpleClientHttpRequestFactory requests=new SimpleClientHttpRequestFactory();requests.setConnectTimeout(Duration.ofSeconds(5));requests.setReadTimeout(Duration.ofSeconds(8));client=RestClient.builder().requestFactory(requests).build();}
 public List<ExternalJobResponse> search(String query,String location){String q=clean(query),l=clean(location);return load().stream().filter(j->q.isEmpty()||contains(j.title(),q)||contains(j.company(),q)||contains(j.skills(),q)).filter(j->l.isEmpty()||contains(j.location(),l)||(l.equals("remote")&&contains(j.location(),"worldwide"))).limit(24).toList();}
 private synchronized List<ExternalJobResponse> load(){if(Instant.now().isBefore(cacheExpires)&&!cached.isEmpty())return cached;try{JsonNode root=client.get().uri(FEED_URL).retrieve().body(JsonNode.class);List<ExternalJobResponse> fresh=new ArrayList<>();if(root!=null)for(JsonNode j:root.path("jobs"))fresh.add(map(j));if(!fresh.isEmpty()){cached=List.copyOf(fresh);cacheExpires=Instant.now().plus(Duration.ofMinutes(15));}}catch(Exception ignored){cacheExpires=Instant.now().plus(Duration.ofMinutes(2));}return cached;}
 private ExternalJobResponse map(JsonNode j){String tags="";if(j.path("tags").isArray()){List<String> values=new ArrayList<>();j.path("tags").forEach(t->values.add(t.asText()));tags=String.join(", ",values);}if(tags.isBlank())tags=text(j,"category");return new ExternalJobResponse("remotive-"+text(j,"id"),text(j,"title"),text(j,"company_name"),text(j,"candidate_required_location"),text(j,"job_type").replace('_',' '),tags,plain(text(j,"description")),safeUrl(text(j,"url")),text(j,"publication_date"),"Remotive");}
 private String text(JsonNode n,String f){return n.path(f).asText("").trim();} private String plain(String h){return HtmlUtils.htmlUnescape(h.replaceAll("<[^>]*>"," ").replaceAll("\\s+"," ")).trim();} private String safeUrl(String url){return url.startsWith("https://remotive.com/")?url:"";} private String clean(String v){return v==null?"":v.trim().toLowerCase(Locale.ROOT);} private boolean contains(String v,String p){return v!=null&&v.toLowerCase(Locale.ROOT).contains(p);}
}
